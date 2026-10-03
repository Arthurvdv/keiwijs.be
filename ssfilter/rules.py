"""Filter configuration and the keep/drop decision for each event."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

from .ical import Component, text_value
from .tags import Tag, TagMatcher, TagSignal

Reason = Literal[
    "exclude_kw",
    "include_kw",
    "untagged_kept",
    "untagged_dropped",
    "tag_match",
    "tag_mismatch",
]

MAX_KEYWORDS = 20
MAX_KEYWORD_LEN = 60


@dataclass(frozen=True)
class FilterConfig:
    tags: tuple[Tag, ...]
    include_untagged: bool = True
    include_keywords: tuple[str, ...] = ()
    exclude_keywords: tuple[str, ...] = ()
    use_organisator: bool = False
    strip_participants: bool = True

    @property
    def selected_names(self) -> frozenset[str]:
        return frozenset(t.name for t in self.tags if t.selected)

    @property
    def label(self) -> str:
        """Short label for the calendar name, e.g. ``L3, L5``."""
        return ", ".join(t.name for t in self.tags if t.selected)


@dataclass(frozen=True)
class Decision:
    keep: bool
    reason: Reason
    detail: str
    signal: TagSignal = field(default_factory=lambda: TagSignal(frozenset(), "none"))


def clean_keywords(words: Sequence[str]) -> tuple[str, ...]:
    out: list[str] = []
    for word in words:
        w = " ".join(str(word).split())
        if w and len(w) <= MAX_KEYWORD_LEN and w.casefold() not in {o.casefold() for o in out}:
            out.append(w)
    if len(out) > MAX_KEYWORDS:
        raise ValueError(f"at most {MAX_KEYWORDS} keywords are allowed")
    return tuple(out)


class RuleEngine:
    """Compiled rules for one configuration."""

    def __init__(self, cfg: FilterConfig):
        self.cfg = cfg
        self.matcher = TagMatcher(cfg.tags)
        self.selected = cfg.selected_names
        self._include = tuple(k.casefold() for k in cfg.include_keywords)
        self._exclude = tuple(k.casefold() for k in cfg.exclude_keywords)

    def decide(self, summary: str, description: str = "") -> Decision:
        haystack = f"{summary}\n{description}".casefold()
        for word in self._exclude:
            if word in haystack:
                return Decision(False, "exclude_kw", word)
        for word in self._include:
            if word in haystack:
                return Decision(True, "include_kw", word)
        signal = self.matcher.match(summary, description, self.cfg.use_organisator)
        if not signal.matched:
            if self.cfg.include_untagged:
                return Decision(True, "untagged_kept", "iedereen" if signal.all_hit else "", signal)
            return Decision(False, "untagged_dropped", "", signal)
        hit = signal.matched & self.selected
        if hit:
            return Decision(True, "tag_match", ", ".join(sorted(hit)), signal)
        return Decision(False, "tag_mismatch", ", ".join(sorted(signal.matched)), signal)

    def decide_event(self, event: Component) -> Decision:
        return self.decide(text_value(event, "SUMMARY"), text_value(event, "DESCRIPTION"))

    def apply(self, calendar: Component) -> tuple[Component, list[tuple[Component, Decision]]]:
        """Return a filtered copy plus the decision for every event (in input order)."""
        out = calendar.clone()
        decisions: list[tuple[Component, Decision]] = []
        kept_children: list[Component] = []
        for child in out.children:
            if child.name != "VEVENT":
                kept_children.append(child)
                continue
            decision = self.decide_event(child)
            decisions.append((child, decision))
            if decision.keep:
                kept_children.append(child)
        out.children = kept_children
        return out, decisions
