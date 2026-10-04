"""Class tags: model, matching against event text, and the yearly rollover.

The tag list is an ordered sequence chosen by the user (default K1..K3, L1..L6).
Matching looks for the tag names (plus Dutch aliases for the well-known ones)
in the event SUMMARY. The rollover moves every selected tag that has
``move_next`` one position further in the *sequence*; the digit in the name
means nothing to the code, only the order does.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from zoneinfo import ZoneInfo

DEFAULT_TAG_NAMES: tuple[str, ...] = ("K1", "K2", "K3", "L1", "L2", "L3", "L4", "L5", "L6")
MAX_TAGS = 30
MAX_TAG_NAME = 40
BRUSSELS = ZoneInfo("Europe/Brussels")
ROLLOVER_HOUR_LOCAL = 3


@dataclass(frozen=True)
class Tag:
    name: str
    selected: bool = False
    move_next: bool = False

    def normalised(self) -> Tag:
        """Enforce the invariant ``move_next => selected`` and trim the name."""
        name = " ".join(self.name.split())
        return Tag(name, self.selected, self.move_next and self.selected)


def default_tags() -> list[Tag]:
    return [Tag(name) for name in DEFAULT_TAG_NAMES]


class TagValidationError(ValueError):
    pass


def validate_tags(tags: Sequence[Tag]) -> list[Tag]:
    """Normalise and validate a user supplied tag list."""
    if not tags:
        raise TagValidationError("at least one tag is required")
    if len(tags) > MAX_TAGS:
        raise TagValidationError(f"at most {MAX_TAGS} tags are allowed")
    out: list[Tag] = []
    seen: set[str] = set()
    for tag in tags:
        norm = tag.normalised()
        if not norm.name:
            raise TagValidationError("tag name may not be empty")
        if len(norm.name) > MAX_TAG_NAME:
            raise TagValidationError(f"tag name longer than {MAX_TAG_NAME} characters")
        key = norm.name.casefold()
        if key in seen:
            raise TagValidationError(f"duplicate tag name: {norm.name}")
        seen.add(key)
        out.append(norm)
    return out


# --------------------------------------------------------------------------- matching

_ORDINALS = {
    1: r"(?:1|1e|1ste|eerste)",
    2: r"(?:2|2e|2de|tweede)",
    3: r"(?:3|3e|3de|derde)",
    4: r"(?:4|4e|4de|vierde)",
    5: r"(?:5|5e|5de|vijfde)",
    6: r"(?:6|6e|6de|zesde)",
}

_KLEUTER_GROUP = re.compile(r"\bkleuter(?:s|tjes|school|klas(?:sen)?|afdeling)?\b")
_LAGER_GROUP = re.compile(r"\blager(?:e school| onderwijs)?\b")
_ALL_GROUP = re.compile(
    r"\b(?:iedereen|hele school|ganse school|alle (?:klassen|leerlingen|kinderen|ouders))\b"
)
_EXCEPT = re.compile(r"\b(?:behalve|uitgezonderd|met uitzondering van|m\.u\.v\.)\s*")
_RANGE = re.compile(
    r"(?<![a-z0-9])([kl])\s?([1-6])\s*(?:-|–|—|t/m|tot(?: en met)?)\s*([kl])?\s?([1-6])(?![a-z0-9])"
)


def _alias_pattern(name: str) -> re.Pattern[str]:
    """Pattern for a tag name: literal with word boundaries plus Dutch aliases for K1..L6."""
    key = name.casefold()
    patterns = [rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])"]
    match = re.fullmatch(r"([kl])([1-6])", key)
    if match:
        letter, digit = match.group(1), int(match.group(2))
        ordinal = _ORDINALS[digit]
        if letter == "k":
            patterns.append(rf"\b{ordinal}\s*kleuter(?:klas|s)?\b")
        else:
            patterns.append(rf"\b{ordinal}\s*leerjaar\b")
    return re.compile("|".join(patterns))


@dataclass(frozen=True)
class TagSignal:
    matched: frozenset[str]
    source: Literal["summary", "organisator", "none"]
    raw: tuple[str, ...] = ()
    all_hit: bool = False
    except_applied: bool = False


class TagMatcher:
    """Compiled matcher for one tag sequence; build once per config."""

    def __init__(self, tags: Sequence[Tag]):
        self.names: tuple[str, ...] = tuple(t.name for t in tags)
        self._index = {n.casefold(): i for i, n in enumerate(self.names)}
        self._patterns = [(n, _alias_pattern(n)) for n in self.names]
        self._all = frozenset(self.names)

    # -- helpers ---------------------------------------------------------
    def _resolve(self, letter: str, digit: str) -> str | None:
        key = f"{letter}{digit}"
        return self.names[self._index[key]] if key in self._index else None

    def _match_fragment(self, text: str) -> tuple[set[str], list[str], bool]:
        found: set[str] = set()
        raws: list[str] = []
        spans: list[tuple[int, int]] = []
        all_hit = False
        for rm in _RANGE.finditer(text):
            l1, d1, l2, d2 = rm.group(1), rm.group(2), rm.group(3) or rm.group(1), rm.group(4)
            start, end = self._resolve(l1, d1), self._resolve(l2, d2)
            if start and end:
                i, j = self._index[start.casefold()], self._index[end.casefold()]
                lo, hi = min(i, j), max(i, j)
                found.update(self.names[lo : hi + 1])
                raws.append(rm.group(0))
                spans.append(rm.span())
        for name, pattern in self._patterns:
            pm = pattern.search(text)
            if pm:
                found.add(name)
                raws.append(pm.group(0))
                spans.append(pm.span())
        # Group words ("kleuters", "lagere school") only count outside explicit matches,
        # so "2de kleuterklas" stays K2 instead of becoming every K tag.
        masked = list(text)
        for a, b in spans:
            masked[a:b] = " " * (b - a)
        remainder = "".join(masked)
        if _KLEUTER_GROUP.search(remainder):
            found.update(n for n in self.names if n.casefold().startswith("k"))
            raws.append("kleuters")
        if _LAGER_GROUP.search(remainder):
            found.update(n for n in self.names if n.casefold().startswith("l"))
            raws.append("lagere school")
        if _ALL_GROUP.search(remainder):
            all_hit = True
            raws.append("iedereen")
        return found, raws, all_hit

    # -- public ----------------------------------------------------------
    def match(
        self, summary: str, description: str = "", use_organisator: bool = False
    ) -> TagSignal:
        text = summary.casefold()
        parts = _EXCEPT.split(text, maxsplit=1)
        before = parts[0]
        after = parts[1] if len(parts) > 1 else None
        found, raws, all_hit = self._match_fragment(before)
        except_applied = False
        if after is not None:
            excluded, raws2, _ = self._match_fragment(after)
            base = set(found) if found and not all_hit else set(self._all)
            found = base - excluded
            raws += [f"behalve {r}" for r in raws2]
            except_applied = True
            all_hit = False
        if all_hit or (found and found == self._all):
            return TagSignal(frozenset(), "summary", tuple(raws), True, except_applied)
        if found:
            return TagSignal(frozenset(found), "summary", tuple(raws), False, except_applied)
        if use_organisator:
            org = self._match_organisator(description)
            if org is not None:
                return org
        return TagSignal(frozenset(), "none", tuple(raws), False, except_applied)

    def _match_organisator(self, description: str) -> TagSignal | None:
        for line in description.split("\n"):
            if not line.casefold().startswith("organisator:"):
                continue
            entries = [e.strip() for e in line.split(":", 1)[1].split(",") if e.strip()]
            hits: set[str] = set()
            raws: list[str] = []
            for entry in entries:
                low = entry.casefold()
                for name, pattern in self._patterns:
                    m = pattern.search(low)
                    if m:
                        hits.add(name)
                        raws.append(m.group(0))
            if len(hits) == 1:
                return TagSignal(frozenset(hits), "organisator", tuple(raws))
            return None
        return None


# --------------------------------------------------------------------------- rollover


@dataclass(frozen=True)
class RolloverReport:
    moved: tuple[tuple[str, str], ...]
    kept: tuple[str, ...]
    dropped_at_end: tuple[str, ...]

    @property
    def changed(self) -> bool:
        return bool(self.moved or self.dropped_at_end)

    def summary(self) -> str:
        bits = [f"{a}→{b}" for a, b in self.moved]
        bits += [f"{n}→(einde)" for n in self.dropped_at_end]
        return ", ".join(bits) if bits else "geen wijzigingen"


def rollover(tags: Sequence[Tag]) -> tuple[list[Tag], RolloverReport]:
    """Move selected tags with ``move_next`` one step along the sequence (snapshot semantics)."""
    selected_next: set[int] = set()
    move_next: set[int] = set()
    moved: list[tuple[str, str]] = []
    kept: list[str] = []
    dropped: list[str] = []
    last = len(tags) - 1
    for i, tag in enumerate(tags):
        if not tag.selected:
            continue
        if tag.move_next:
            if i < last:
                selected_next.add(i + 1)
                move_next.add(i + 1)
                moved.append((tag.name, tags[i + 1].name))
            else:
                dropped.append(tag.name)
        else:
            selected_next.add(i)
            kept.append(tag.name)
    new_tags = [
        Tag(t.name, i in selected_next, i in move_next and i in selected_next)
        for i, t in enumerate(tags)
    ]
    return new_tags, RolloverReport(tuple(moved), tuple(kept), tuple(dropped))


# --------------------------------------------------------------------------- scheduling

_MONTH_DAY = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")


def validate_month_day(value: str) -> str:
    if not _MONTH_DAY.match(value):
        raise TagValidationError("rollover date must be MM-DD")
    month, day = int(value[:2]), int(value[3:])
    if day > _days_in_month(month, leap=True):
        raise TagValidationError("invalid day for month")
    return value


def _days_in_month(month: int, *, leap: bool) -> int:
    return [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]


def next_rollover_utc(month_day: str, after: datetime) -> datetime:
    """First occurrence of ``month_day`` at 03:00 Europe/Brussels strictly after ``after``.

    Feb 29 on a non-leap year falls back to Feb 28.
    """
    if after.tzinfo is None:
        raise ValueError("after must be timezone-aware")
    month, day = int(month_day[:2]), int(month_day[3:])
    local_after = after.astimezone(BRUSSELS)
    for year in (local_after.year, local_after.year + 1, local_after.year + 2):
        d = min(day, _days_in_month(month, leap=_is_leap(year)))
        candidate = datetime(year, month, d, ROLLOVER_HOUR_LOCAL, 0, 0, tzinfo=BRUSSELS)
        if candidate > local_after:
            return candidate.astimezone(UTC)
    raise AssertionError("unreachable")


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def tags_from_json(items: Iterable[dict[str, object]]) -> list[Tag]:
    out: list[Tag] = []
    for item in items:
        name = str(item.get("name", ""))
        out.append(Tag(name, bool(item.get("selected", False)), bool(item.get("moveNext", False))))
    return out


def tags_to_json(tags: Sequence[Tag]) -> list[dict[str, object]]:
    return [{"name": t.name, "selected": t.selected, "moveNext": t.move_next} for t in tags]
