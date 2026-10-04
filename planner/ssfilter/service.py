"""Application service: the operations behind the HTTP API, independent of Azure Functions."""

from __future__ import annotations

import logging
import time
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from . import ical
from .config import Settings
from .fetcher import UpstreamError, fetch_ics, new_client, normalise_url
from .icons import summary_icon
from .models import FeedConfig, row_key_for
from .publisher import BlobFeedPublisher, FeedPublisher
from .renderer import FAILING_THRESHOLD, Renderer, RenderResult
from .rules import RuleEngine
from .store import FeedRepository, TableFeedRepository
from .tags import TagValidationError

log = logging.getLogger("ssfilter.service")

PREVIEW_CACHE_TTL = 60.0
MAX_PREVIEW_EVENTS = 400


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


@dataclass
class App:
    settings: Settings
    repo: FeedRepository
    publisher: FeedPublisher
    client: httpx.AsyncClient
    renderer: Renderer

    def __post_init__(self) -> None:
        self._upstream_cache: dict[str, tuple[float, bytes]] = {}

    # ------------------------------------------------------------------ construction
    @classmethod
    def build(cls, settings: Settings) -> App:
        repo = TableFeedRepository.from_settings(settings)
        publisher = BlobFeedPublisher.from_settings(settings)
        if (
            settings.storage_connection_string
            and "devstoreaccount1"
            in settings.storage_connection_string.lower() + settings.feed_base_url.lower()
        ):
            # Azurite: create tables and the $web container on first use.
            repo.ensure_tables()
            publisher.ensure_container()
        else:
            repo.ensure_tables()
        client = new_client()
        return cls(settings, repo, publisher, client, Renderer(repo, publisher, settings, client))

    @classmethod
    def for_tests(
        cls,
        settings: Settings,
        repo: FeedRepository,
        publisher: FeedPublisher,
        client: httpx.AsyncClient,
    ) -> App:
        return cls(settings, repo, publisher, client, Renderer(repo, publisher, settings, client))

    # ------------------------------------------------------------------ helpers
    def normalise(self, url: Any) -> str:
        if not isinstance(url, str):
            raise ApiError(400, "invalid_url", "url must be a string")
        try:
            return normalise_url(url, self.settings.host_pattern, self.settings.path_pattern)
        except UpstreamError as exc:
            raise ApiError(400, "invalid_url", str(exc)) from exc

    async def _upstream(self, normalised_url: str) -> ical.Component:
        key = row_key_for(normalised_url)
        now = time.monotonic()
        cached = self._upstream_cache.get(key)
        if cached and cached[0] > now:
            body = cached[1]
        else:
            try:
                upstream = await fetch_ics(
                    normalised_url,
                    self.client,
                    user_agent=self.settings.user_agent,
                    host_pattern=self.settings.host_pattern,
                    path_pattern=self.settings.path_pattern,
                )
            except UpstreamError as exc:
                status = 400 if exc.kind in ("invalid_url", "blocked") else 502
                raise ApiError(status, f"upstream_{exc.kind}", str(exc)) from exc
            body = upstream.body
            if len(self._upstream_cache) > 64:
                self._upstream_cache.clear()
            self._upstream_cache[key] = (now + PREVIEW_CACHE_TTL, body)
        try:
            return ical.parse(body)
        except ical.IcsParseError as exc:
            raise ApiError(502, "upstream_not_ics", str(exc)) from exc

    def _config_for(self, normalised_url: str) -> tuple[FeedConfig, bool]:
        existing = self.repo.get_by_url(normalised_url)
        if existing:
            return existing, True
        return FeedConfig.new(normalised_url), False

    # ------------------------------------------------------------------ operations
    async def inspect(self, url: Any) -> dict[str, Any]:
        normalised = self.normalise(url)
        cfg, existing = self._config_for(normalised)
        calendar = await self._upstream(normalised)
        return {
            "existing": existing,
            "settings": cfg.settings_dto(),
            "feedUrl": self.publisher.url_for(cfg.row_key),
            "rowKey": cfg.row_key,
            "lastRenderedUtc": cfg.last_rendered_utc.isoformat() if cfg.last_rendered_utc else None,
            **self._preview(calendar, cfg),
        }

    async def preview(self, url: Any, settings: Mapping[str, Any] | None) -> dict[str, Any]:
        normalised = self.normalise(url)
        cfg, _ = self._config_for(normalised)
        if settings is not None:
            cfg = self._apply_settings(cfg, settings)
        calendar = await self._upstream(normalised)
        return self._preview(calendar, cfg)

    async def save(self, url: Any, settings: Mapping[str, Any]) -> dict[str, Any]:
        normalised = self.normalise(url)
        cfg, existing = self._config_for(normalised)
        cfg = self._apply_settings(cfg, settings)
        cfg.content_hash = ""  # force a publish so the blob reflects the new settings right away
        self.repo.upsert(cfg)
        result = await self.renderer.render_one(cfg, trigger="save")
        self._upstream_cache.pop(cfg.row_key, None)
        return {
            "created": not existing,
            "rowKey": cfg.row_key,
            "feedUrl": self.publisher.url_for(cfg.row_key),
            "webcalUrl": _webcal(self.publisher.url_for(cfg.row_key)),
            "settings": cfg.settings_dto(),
            "render": _render_dto(result),
        }

    def delete(self, url: Any) -> bool:
        normalised = self.normalise(url)
        existing = self.repo.get_by_url(normalised)
        if not existing:
            return False
        self.publisher.unpublish(existing.row_key)
        self.repo.delete(existing)
        self._upstream_cache.pop(existing.row_key, None)
        return True

    async def render_by_row_key(self, row_key: str) -> RenderResult | None:
        cfg = self.repo.get(row_key)
        if cfg is None:
            return None
        return await self.renderer.render_one(cfg, trigger="admin")

    def health(self) -> dict[str, Any]:
        failing = self.repo.count_failing(FAILING_THRESHOLD)
        return {"status": "ok", "failingFeeds": failing}

    # ------------------------------------------------------------------ internals
    def _apply_settings(self, cfg: FeedConfig, settings: Mapping[str, Any]) -> FeedConfig:
        if not isinstance(settings, Mapping):
            raise ApiError(400, "invalid_settings", "settings must be an object")
        try:
            return cfg.with_settings(settings)
        except TagValidationError as exc:
            raise ApiError(400, "invalid_settings", str(exc)) from exc

    def _preview(self, calendar: ical.Component, cfg: FeedConfig) -> dict[str, Any]:
        engine = RuleEngine(cfg.filter_config())
        hits: Counter[str] = Counter()
        rows: list[dict[str, Any]] = []
        kept = 0
        events = sorted(calendar.events(), key=_sort_key)
        for event in events[:MAX_PREVIEW_EVENTS]:
            summary = ical.text_value(event, "SUMMARY")
            description = ical.text_value(event, "DESCRIPTION")
            decision = engine.decide(summary, description)
            for name in decision.signal.matched:
                hits[name] += 1
            kept += int(decision.keep)
            rows.append(
                {
                    "uid": ical.text_value(event, "UID"),
                    "start": _when(event, "DTSTART"),
                    "end": _when(event, "DTEND"),
                    "allDay": _is_all_day(event),
                    "summary": summary,
                    "icon": summary_icon(summary, cfg.icon_rules, cfg.fallback_icon)
                    if cfg.title_icons
                    else None,
                    "tags": sorted(decision.signal.matched),
                    "keep": decision.keep,
                    "reason": decision.reason,
                    "detail": decision.detail,
                }
            )
        return {
            "calendarName": ical.text_value(calendar, "X-WR-CALNAME"),
            "eventCount": len(events),
            "keptCount": kept,
            "tagHits": {t.name: hits.get(t.name, 0) for t in cfg.tags},
            "events": rows,
        }


def _webcal(url: str) -> str:
    return "webcal://" + url.split("://", 1)[1] if "://" in url else url


def _render_dto(result: RenderResult) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "changed": result.changed,
        "eventCount": result.event_count,
        "error": result.error,
        "rollovers": [r.summary() for r in result.rollovers],
    }


def _is_all_day(event: ical.Component) -> bool:
    prop = event.get("DTSTART")
    return bool(prop and prop.params.get("VALUE") == "DATE")


def _when(event: ical.Component, name: str) -> str | None:
    prop = event.get(name)
    if prop is None:
        return None
    value = prop.value.strip()
    if prop.params.get("VALUE") == "DATE" and len(value) == 8:
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    if len(value) >= 15 and value[8] == "T":
        base = f"{value[:4]}-{value[4:6]}-{value[6:8]}T{value[9:11]}:{value[11:13]}:{value[13:15]}"
        return base + ("Z" if value.endswith("Z") else "")
    return value


def _sort_key(event: ical.Component) -> str:
    prop = event.get("DTSTART")
    return prop.value if prop else ""
