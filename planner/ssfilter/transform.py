"""Output transforms applied after filtering, plus the change fingerprint."""

from __future__ import annotations

import hashlib

from .ical import Component, escape_text, make_line, serialize, text_value, unfold
from .icons import decorate_description, prefix_summary
from .rules import FilterConfig

PARTICIPANTS_PREFIX = "extra deelnemers:"
DEFAULT_TTL = "PT1H"
DEFAULT_CALNAME = "Smartschool Planner"


def strip_extra_deelnemers(description: str) -> tuple[str, bool]:
    """Remove ``Extra deelnemers:`` lines (pupil names). Returns (text, changed)."""
    lines = description.split("\n")
    kept = [ln for ln in lines if not ln.casefold().lstrip().startswith(PARTICIPANTS_PREFIX)]
    if len(kept) == len(lines):
        return description, False
    return "\n".join(kept), True


def apply_event_transforms(event: Component, cfg: FilterConfig) -> None:
    prop = event.get("DESCRIPTION")
    if prop is not None:
        original = text_value(event, "DESCRIPTION")
        text = original
        if cfg.strip_participants:
            text, _ = strip_extra_deelnemers(text)
        text = decorate_description(text, drop_labels=cfg.title_icons)
        if text != original:
            event.set(prop.with_value(escape_text(text)))
    summary = event.get("SUMMARY")
    if cfg.title_icons and summary is not None:
        original = text_value(event, "SUMMARY")
        titled = prefix_summary(original, cfg.icon_rules, cfg.fallback_icon)
        if titled != original:
            event.set(summary.with_value(escape_text(titled)))


def set_calname(calendar: Component, suffix: str) -> None:
    original = text_value(calendar, "X-WR-CALNAME") or DEFAULT_CALNAME
    name = f"{original} ({suffix})" if suffix else original
    calendar.set(make_line("X-WR-CALNAME", escape_text(name)))


def ensure_ttl(calendar: Component, ttl: str = DEFAULT_TTL) -> None:
    if calendar.get("REFRESH-INTERVAL") is None:
        calendar.set(make_line("REFRESH-INTERVAL", ttl, {"VALUE": "DURATION"}))
    if calendar.get("X-PUBLISHED-TTL") is None:
        calendar.set(make_line("X-PUBLISHED-TTL", ttl))


def finalize(calendar: Component, cfg: FilterConfig) -> Component:
    """Mutate the (already filtered) calendar into its published form."""
    for event in calendar.events():
        apply_event_transforms(event, cfg)
    set_calname(calendar, cfg.label)
    ensure_ttl(calendar)
    return calendar


def render(calendar: Component, cfg: FilterConfig) -> bytes:
    return serialize(finalize(calendar, cfg))


def content_fingerprint(data: bytes) -> str:
    """SHA-256 over the logical lines, ignoring DTSTAMP (SmartSchool regenerates it per fetch)."""
    digest = hashlib.sha256()
    for line in unfold(data):
        if line.upper().startswith("DTSTAMP"):
            continue
        digest.update(line.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()
