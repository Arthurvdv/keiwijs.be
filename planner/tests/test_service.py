from __future__ import annotations

import httpx
import pytest
import respx

from ssfilter import fetcher
from ssfilter.config import Settings
from ssfilter.http import RateLimiter
from ssfilter.publisher import InMemoryFeedPublisher, blob_name
from ssfilter.service import ApiError, App
from ssfilter.store import InMemoryFeedRepository

URL = (
    "https://school.smartschool.be/planner/sync/ics/"
    "e2ed7bf1-269c-499b-ba8a-5ddc3596d59c/e0c9355d-6573-518e-82e0-888b9d33e772"
)


@pytest.fixture(autouse=True)
def _no_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    async def ok(_host: str) -> None:
        return None

    monkeypatch.setattr(fetcher, "assert_public_host", ok)


@pytest.fixture()
def app() -> App:
    settings = Settings.from_env({"FEED_BASE_URL": "https://acct.z6.web.core.windows.net"})
    return App.for_tests(
        settings,
        InMemoryFeedRepository(),
        InMemoryFeedPublisher(settings.feed_base_url),
        httpx.AsyncClient(),
    )


def _settings(selected: list[str], **extra: object) -> dict[str, object]:
    tags = [
        {"name": n, "selected": n in selected, "moveNext": n in selected}
        for n in ("K1", "K2", "K3", "L1", "L2", "L3", "L4", "L5", "L6")
    ]
    return {"tags": tags, "includeUntagged": True, "rolloverMonthDay": "07-01", **extra}


@respx.mock
async def test_inspect_new_feed(app: App, fixture_bytes: bytes) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    data = await app.inspect(URL + "/")
    assert data["existing"] is False
    assert data["eventCount"] == 90
    assert data["calendarName"] == "GMail"
    assert data["tagHits"]["L2"] == 17 and data["tagHits"]["K1"] == 1
    assert data["settings"]["tags"][0] == {"name": "K1", "selected": False, "moveNext": False}
    assert data["settings"]["rolloverMonthDay"] == "08-01"
    assert data["settings"]["titleIcons"] is True
    assert data["settings"]["fallbackIcon"] == "📌"
    assert data["settings"]["iconRules"][0] == {"keyword": "vakantie", "icon": "☀️"}
    assert data["feedUrl"].startswith("https://acct.z6.web.core.windows.net/feeds/")
    # nothing selected yet: only untagged items are kept
    assert data["keptCount"] == 48
    first = data["events"][0]
    assert set(first) >= {"uid", "start", "summary", "tags", "keep", "reason", "detail", "allDay"}
    assert first["start"] == "2026-09-03T16:00:00Z" and first["allDay"] is False
    icons = {e["summary"]: e["icon"] for e in data["events"]}
    assert icons["L3: Bib"] == "📚" and icons["Kerstvakantie"] == "☀️"
    assert icons["Paaslunch"] == "📌"


@respx.mock
async def test_save_then_inspect_loads_existing(app: App, fixture_bytes: bytes) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    saved = await app.save(URL, _settings(["L3"], excludeKeywords=["fluo"]))
    assert saved["created"] is True and saved["render"]["ok"] is True
    assert saved["render"]["eventCount"] == 63  # 64 minus the fluo event
    assert saved["webcalUrl"].startswith("webcal://acct.z6.web.core.windows.net/feeds/")
    row_key = saved["rowKey"]
    pub = app.publisher
    assert isinstance(pub, InMemoryFeedPublisher) and blob_name(row_key) in pub.blobs

    again = await app.inspect(URL)
    assert again["existing"] is True
    assert [t["name"] for t in again["settings"]["tags"] if t["selected"]] == ["L3"]
    assert again["settings"]["excludeKeywords"] == ["fluo"]
    assert again["keptCount"] == 63

    # saving again upserts without complaint and re-renders
    saved2 = await app.save(URL, _settings(["L2", "L4"]))
    assert saved2["created"] is False and saved2["rowKey"] == row_key
    assert saved2["render"]["changed"] is True


@respx.mock
async def test_preview_with_settings_does_not_persist(app: App, fixture_bytes: bytes) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    data = await app.preview(URL, _settings(["L3"], includeUntagged=False))
    assert data["keptCount"] == 16
    assert app.repo.get_by_url(URL) is None


@respx.mock
async def test_delete(app: App, fixture_bytes: bytes) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    assert app.delete(URL) is False
    saved = await app.save(URL, _settings(["L1"]))
    assert app.delete(URL) is True
    pub = app.publisher
    assert isinstance(pub, InMemoryFeedPublisher) and blob_name(saved["rowKey"]) not in pub.blobs
    assert app.repo.get_by_url(URL) is None


@respx.mock
async def test_validation_errors(app: App, fixture_bytes: bytes) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    with pytest.raises(ApiError) as exc:
        await app.inspect("https://evil.com/x")
    assert exc.value.status == 400 and exc.value.code == "invalid_url"
    with pytest.raises(ApiError) as exc:
        await app.save(URL, {"tags": [{"name": "L1"}, {"name": "l1"}]})
    assert exc.value.code == "invalid_settings"
    with pytest.raises(ApiError) as exc:
        await app.save(URL, _settings(["L1"], rolloverMonthDay="31-12"))
    assert exc.value.code == "invalid_settings"
    with pytest.raises(ApiError) as exc:
        await app.save(URL, {"tags": "nope"})
    assert exc.value.code == "invalid_settings"
    with pytest.raises(ApiError) as exc:
        await app.save(URL, _settings(["L1"], iconRules=[{"keyword": "", "icon": "x"}]))
    assert exc.value.code == "invalid_settings"


@respx.mock
async def test_icon_settings_round_trip(app: App, fixture_bytes: bytes) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    rules = [{"keyword": "Bib", "icon": "☀"}, {"keyword": "toets", "icon": "📝"}]
    await app.save(URL, _settings(["L3"], titleIcons=False, iconRules=rules, fallbackIcon=""))
    again = await app.inspect(URL)
    assert again["settings"]["titleIcons"] is False
    assert again["settings"]["fallbackIcon"] == ""
    # the lone text-presentation sun gets VS16 so it renders full width
    assert again["settings"]["iconRules"][0] == {"keyword": "Bib", "icon": "☀️"}
    assert all(e["icon"] is None for e in again["events"])


@respx.mock
async def test_upstream_failures_map_to_502(app: App) -> None:
    respx.get(URL).mock(return_value=httpx.Response(500))
    with pytest.raises(ApiError) as exc:
        await app.inspect(URL)
    assert exc.value.status == 502 and exc.value.code == "upstream_http_status"


@respx.mock
async def test_move_next_requires_selected(app: App, fixture_bytes: bytes) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=fixture_bytes))
    settings = _settings(["L1"])
    settings["tags"][1]["moveNext"] = True  # K2 not selected but moveNext ticked
    saved = await app.save(URL, settings)
    k2 = [t for t in saved["settings"]["tags"] if t["name"] == "K2"][0]
    assert k2 == {"name": "K2", "selected": False, "moveNext": False}


def test_rate_limiter() -> None:
    limiter = RateLimiter(rate_per_minute=60, burst=3)
    assert [limiter.allow("a", now=0.0) for _ in range(4)] == [True, True, True, False]
    assert limiter.allow("b", now=0.0) is True
    assert limiter.allow("a", now=1.0) is True  # one token refilled after a second
