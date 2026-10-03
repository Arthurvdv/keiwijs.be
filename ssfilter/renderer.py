"""Render pipeline: rollover-if-due -> fetch -> filter -> finalize -> publish-if-changed."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

import httpx

from . import ical
from .config import Settings
from .fetcher import UpstreamError, fetch_ics
from .models import FeedConfig, RolloverLogEntry, utcnow
from .publisher import FeedPublisher
from .rules import RuleEngine
from .store import FeedRepository
from .tags import RolloverReport, next_rollover_utc, rollover
from .transform import content_fingerprint, render

log = logging.getLogger("ssfilter.renderer")

MAX_CATCHUP_ROLLOVERS = 5
FAILING_THRESHOLD = 30


@dataclass(frozen=True)
class RenderResult:
    row_key: str
    ok: bool
    changed: bool = False
    event_count: int | None = None
    error: str | None = None
    rollovers: tuple[RolloverReport, ...] = ()


@dataclass
class RenderSummary:
    total: int = 0
    ok: int = 0
    changed: int = 0
    failed: int = 0
    rolled_over: int = 0
    errors: list[tuple[str, str]] = field(default_factory=list)  # (row_key[:8], message)


class Renderer:
    def __init__(
        self,
        repo: FeedRepository,
        publisher: FeedPublisher,
        settings: Settings,
        client: httpx.AsyncClient,
        now: Callable[[], datetime] = utcnow,
    ):
        self.repo = repo
        self.publisher = publisher
        self.settings = settings
        self.client = client
        self.now = now

    # ------------------------------------------------------------------ rollover
    def apply_due_rollovers(
        self, cfg: FeedConfig, trigger: str = "render"
    ) -> tuple[RolloverReport, ...]:
        """Move tags for every rollover date that has passed (persisted immediately)."""
        reports: list[RolloverReport] = []
        now = self.now()
        for _ in range(MAX_CATCHUP_ROLLOVERS):
            if cfg.next_rollover_utc > now:
                break
            before = list(cfg.tags)
            new_tags, report = rollover(cfg.tags)
            cfg.tags = new_tags
            cfg.last_rollover_utc = now
            cfg.next_rollover_utc = next_rollover_utc(cfg.rollover_month_day, cfg.next_rollover_utc)
            cfg.updated_utc = now
            self.repo.upsert(cfg)
            self.repo.log_rollover(
                RolloverLogEntry(cfg.row_key, now, trigger, before, new_tags, report.summary())
            )
            reports.append(report)
            log.info("rollover %s: %s", cfg.row_key[:8], report.summary())
        return tuple(reports)

    # ------------------------------------------------------------------ one feed
    async def render_one(self, cfg: FeedConfig, trigger: str = "render") -> RenderResult:
        rollovers = self.apply_due_rollovers(cfg, trigger)
        now = self.now()
        try:
            upstream = await fetch_ics(
                cfg.source_url,
                self.client,
                user_agent=self.settings.user_agent,
                host_pattern=self.settings.host_pattern,
                path_pattern=self.settings.path_pattern,
            )
            calendar = ical.parse(upstream.body)
            filter_config = cfg.filter_config()
            filtered, _decisions = RuleEngine(filter_config).apply(calendar)
            body = render(filtered, filter_config)
        except UpstreamError as exc:
            message = f"{exc.kind}: {exc}"
            self.repo.mark_rendered(cfg, content_hash=None, changed=False, error=message, now=now)
            log.warning("render %s failed: %s", cfg.row_key[:8], message)
            return RenderResult(cfg.row_key, False, error=message, rollovers=rollovers)
        except ical.IcsParseError as exc:
            message = f"parse: {exc}"
            self.repo.mark_rendered(cfg, content_hash=None, changed=False, error=message, now=now)
            log.warning("render %s failed: %s", cfg.row_key[:8], message)
            return RenderResult(cfg.row_key, False, error=message, rollovers=rollovers)

        fingerprint = content_fingerprint(body)
        changed = fingerprint != cfg.content_hash
        if changed:
            self.publisher.publish(cfg.row_key, body)
        self.repo.mark_rendered(cfg, content_hash=fingerprint, changed=changed, error=None, now=now)
        count = sum(1 for _ in filtered.events())
        log.info("render %s ok changed=%s events=%d", cfg.row_key[:8], changed, count)
        return RenderResult(cfg.row_key, True, changed, count, rollovers=rollovers)

    # ------------------------------------------------------------------ all feeds
    async def render_all(self, concurrency: int = 5) -> RenderSummary:
        summary = RenderSummary()
        semaphore = asyncio.Semaphore(concurrency)

        async def guarded(cfg: FeedConfig) -> None:
            async with semaphore:
                summary.total += 1
                try:
                    result = await self.render_one(cfg)
                except Exception as exc:  # noqa: BLE001 - one bad feed must not stop the run
                    log.exception("render %s crashed", cfg.row_key[:8])
                    summary.failed += 1
                    summary.errors.append((cfg.row_key[:8], f"crash: {exc.__class__.__name__}"))
                    return
                if result.ok:
                    summary.ok += 1
                    summary.changed += int(result.changed)
                else:
                    summary.failed += 1
                    summary.errors.append((cfg.row_key[:8], result.error or "unknown"))
                summary.rolled_over += int(any(r.changed for r in result.rollovers))

        await asyncio.gather(*(guarded(cfg) for cfg in self.repo.list_all()))
        log.info(
            "render_all total=%d ok=%d changed=%d failed=%d rolled_over=%d",
            summary.total,
            summary.ok,
            summary.changed,
            summary.failed,
            summary.rolled_over,
        )
        return summary
