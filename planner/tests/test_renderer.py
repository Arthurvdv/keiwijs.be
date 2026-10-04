from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import pytest
import respx

from ssfilter import fetcher
from ssfilter.config import Settings
from ssfilter.models import FeedConfig
from ssfilter.publisher import InMemoryFeedPublisher, blob_name
from ssfilter.renderer import Renderer
from ssfilter.store import InMemoryFeedRepository
from ssfilter.tags import Tag

URL = (
    "https://school.smartschool.be/planner/sync/ics/"
    "e2ed7bf1-269c-499b-ba8a-5ddc3596d59c/e0c9355d-6573-518e-82e0-888b9d33e772"
)
NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _no_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    async def ok(_host: str) -> None:
        return None

    monkeypatch.setattr(fetcher, "assert_public_host", ok)


class Clock:
    def __init__(self, at: datetime):
        self.at = at

    def __call__(self) -> datetime:
        return self.at


@pytest.fixture()
def world() -> tuple[
    Renderer, InMemoryFeedRepository, InMemoryFeedPublisher, Clock, httpx.AsyncClient
]:
    repo = InMemoryFeedRepository()
    pub = InMemoryFeedPublisher()
    clock = Clock(NOW)
    client = httpx.AsyncClient()
    renderer = Renderer(repo, pub, Settings.from_env({}), client, now=clock)
    return renderer, repo, pub, clock, client


def _cfg(selected: str = "L3", now: datetime = NOW) -> FeedConfig:
    cfg = FeedConfig.new(URL, now)
    cfg.tags = [Tag(t.name, t.name == selected, t.name == selected) for t in cfg.tags]
    return cfg


@respx.mock
async def test_render_publishes_once_until_content_changes(world, fixture_bytes: bytes) -> None:
    renderer, repo, pub, clock, _ = world
    cfg = _cfg()
    repo.upsert(cfg)
    route = respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))

    first = await renderer.render_one(cfg)
    assert first.ok and first.changed and first.event_count == 64
    assert pub.publish_calls == 1
    stored = repo.get(cfg.row_key)
    assert stored and stored.content_hash and stored.last_rendered_utc == NOW
    assert stored.last_changed_utc == NOW and stored.consecutive_errors == 0

    # upstream regenerates DTSTAMP every fetch; that must not count as a change
    restamped = fixture_bytes.replace(b"DTSTAMP:20261003T082130Z", b"DTSTAMP:20261003T090000Z")
    route.mock(return_value=httpx.Response(200, content=restamped))
    clock.at = NOW + timedelta(hours=1)
    second = await renderer.render_one(repo.get(cfg.row_key))  # type: ignore[arg-type]
    assert second.ok and not second.changed
    assert pub.publish_calls == 1
    assert repo.get(cfg.row_key).last_changed_utc == NOW  # type: ignore[union-attr]

    route.mock(
        return_value=httpx.Response(200, content=fixture_bytes.replace(b"L3: Bib", b"L3: Bieb"))
    )
    third = await renderer.render_one(repo.get(cfg.row_key))  # type: ignore[arg-type]
    assert third.changed and pub.publish_calls == 2
    assert b"L3: Bieb" in pub.blobs[blob_name(cfg.row_key)]


@respx.mock
async def test_upstream_failure_keeps_previous_blob(world, fixture_bytes: bytes) -> None:
    renderer, repo, pub, clock, _ = world
    cfg = _cfg()
    repo.upsert(cfg)
    route = respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    await renderer.render_one(cfg)
    blob_before = pub.blobs[blob_name(cfg.row_key)]

    route.mock(return_value=httpx.Response(503))
    clock.at = NOW + timedelta(hours=1)
    result = await renderer.render_one(repo.get(cfg.row_key))  # type: ignore[arg-type]
    assert not result.ok and result.error and "http_status" in result.error
    stored = repo.get(cfg.row_key)
    assert stored and stored.consecutive_errors == 1 and stored.last_error
    assert stored.last_error_utc == clock.at and stored.last_rendered_utc == NOW
    assert pub.blobs[blob_name(cfg.row_key)] == blob_before

    route.mock(return_value=httpx.Response(200, content=b"<html>"))
    result = await renderer.render_one(repo.get(cfg.row_key))  # type: ignore[arg-type]
    assert not result.ok and repo.get(cfg.row_key).consecutive_errors == 2  # type: ignore[union-attr]

    route.mock(return_value=httpx.Response(200, content=fixture_bytes))
    result = await renderer.render_one(repo.get(cfg.row_key))  # type: ignore[arg-type]
    assert result.ok and repo.get(cfg.row_key).consecutive_errors == 0  # type: ignore[union-attr]


@respx.mock
async def test_due_rollover_is_applied_before_filtering(world, fixture_bytes: bytes) -> None:
    renderer, repo, pub, clock, _ = world
    cfg = _cfg("L2")
    cfg.next_rollover_utc = NOW - timedelta(days=1)
    repo.upsert(cfg)
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))

    result = await renderer.render_one(cfg)
    assert result.ok and len(result.rollovers) == 1
    assert result.rollovers[0].moved == (("L2", "L3"),)
    stored = repo.get(cfg.row_key)
    assert stored is not None
    assert [t.name for t in stored.tags if t.selected] == ["L3"]
    assert stored.last_rollover_utc == NOW
    assert stored.next_rollover_utc > NOW
    assert stored.next_rollover_utc.year == 2027
    assert len(repo.rollover_log) == 1 and repo.rollover_log[0].summary == "L2→L3"
    # the published blob is the L3 view (16 L3 events + 48 untagged)
    assert result.event_count == 64

    # running again in the same hour must not roll twice
    again = await renderer.render_one(repo.get(cfg.row_key))  # type: ignore[arg-type]
    assert again.rollovers == ()


@respx.mock
async def test_catch_up_rollovers_are_bounded(world, fixture_bytes: bytes) -> None:
    renderer, repo, pub, clock, _ = world
    cfg = _cfg("K1")
    cfg.next_rollover_utc = NOW - timedelta(days=365 * 3)
    repo.upsert(cfg)
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    result = await renderer.render_one(cfg)
    names = [t.name for t in repo.get(cfg.row_key).tags if t.selected]  # type: ignore[union-attr]
    assert len(result.rollovers) == 4 and names == ["L2"]  # stale date + 2024, 2025, 2026


@respx.mock
async def test_render_all_isolates_failures(world, fixture_bytes: bytes) -> None:
    renderer, repo, pub, clock, _ = world
    good = _cfg("L3")
    bad = FeedConfig.new(URL.replace("e0c9355d", "bbbbbbbb"), NOW)
    repo.upsert(good)
    repo.upsert(bad)
    respx.get(good.source_url).mock(return_value=httpx.Response(200, content=fixture_bytes))
    respx.get(bad.source_url).mock(side_effect=httpx.ConnectError("boom"))
    summary = await renderer.render_all(concurrency=2)
    assert summary.total == 2 and summary.ok == 1 and summary.failed == 1
    assert summary.changed == 1 and summary.errors[0][1].startswith("network")
