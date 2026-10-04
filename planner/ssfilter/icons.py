"""Emoji icons for the published feed.

The Smartschool export has no item-type field, so the title icon comes from an
ordered list of user keyword rules (first match wins, otherwise a fallback).
Description lines with a known ``Label:`` always get a fixed icon. Calendar
apps only render Unicode in SUMMARY/DESCRIPTION, hence emoji instead of images.
Icon and text are always separated by exactly one U+0020 space.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .tags import TagValidationError

MAX_ICON_RULES = 30
MAX_ICON_KEYWORD = 40
MAX_ICON_LEN = 16
VS16 = "️"


@dataclass(frozen=True)
class IconRule:
    keyword: str
    icon: str

    def to_json(self) -> dict[str, str]:
        return {"keyword": self.keyword, "icon": self.icon}


DEFAULT_ICON_RULES: tuple[IconRule, ...] = (
    IconRule("vakantie", "☀️"),
    IconRule("geen school", "☀️"),
    IconRule("studiedag", "☀️"),
    IconRule("bib", "📚"),
    IconRule("toets", "📝"),
    IconRule("rapport", "📄"),
    IconRule("oudercontact", "👥"),
    IconRule("vaccin", "💉"),
    IconRule("zeeklassen", "🌊"),
    IconRule("bosklassen", "🌲"),
    IconRule("schoolfeest", "🎉"),
    IconRule("uitstap", "🚌"),
    IconRule("zwemmen", "🏊"),
)
DEFAULT_FALLBACK_ICON = "📌"

# Fixed icons for the ``Label: value`` lines Smartschool puts in DESCRIPTION.
LABEL_ICONS: Mapping[str, str] = {
    "kalender": "🗓️",
    "organisator": "👤",
    "deelnemers": "👥",
    "extra deelnemers": "👥",
    "weblink": "🔗",
    "organisatie of verloop": "📝",
}

# Supplementary-plane symbols that default to *text* presentation (narrow glyph)
# and therefore need VS16. Basic-plane symbols are handled by the code-point check.
_TEXT_DEFAULT_SMP = frozenset(
    {
        0x1F321, 0x1F324, 0x1F325, 0x1F326, 0x1F327, 0x1F328, 0x1F329, 0x1F32A, 0x1F32B,
        0x1F32C, 0x1F336, 0x1F37D, 0x1F396, 0x1F397, 0x1F399, 0x1F39A, 0x1F39B, 0x1F39E,
        0x1F39F, 0x1F3CB, 0x1F3CC, 0x1F3CD, 0x1F3CE, 0x1F3D4, 0x1F3D5, 0x1F3D6, 0x1F3D7,
        0x1F3D8, 0x1F3D9, 0x1F3DA, 0x1F3DB, 0x1F3DC, 0x1F3DD, 0x1F3DE, 0x1F3DF, 0x1F3F3,
        0x1F3F5, 0x1F3F7, 0x1F43F, 0x1F441, 0x1F4FD, 0x1F549, 0x1F54A, 0x1F56F, 0x1F570,
        0x1F573, 0x1F574, 0x1F575, 0x1F576, 0x1F577, 0x1F578, 0x1F579, 0x1F587, 0x1F58A,
        0x1F58B, 0x1F58C, 0x1F58D, 0x1F590, 0x1F5A5, 0x1F5A8, 0x1F5B1, 0x1F5B2, 0x1F5BC,
        0x1F5C2, 0x1F5C3, 0x1F5C4, 0x1F5D1, 0x1F5D2, 0x1F5D3, 0x1F5DC, 0x1F5DD, 0x1F5DE,
        0x1F5E1, 0x1F5E3, 0x1F5E8, 0x1F5EF, 0x1F5F3, 0x1F5FA, 0x1F6CB, 0x1F6CD, 0x1F6CE,
        0x1F6CF, 0x1F6E0, 0x1F6E1, 0x1F6E2, 0x1F6E3, 0x1F6E4, 0x1F6E5, 0x1F6E9, 0x1F6F0,
        0x1F6F3,
    }
)  # fmt: skip


def normalise_icon(raw: str) -> str:
    """Trim, and add VS16 to a lone text-presentation symbol (``☀`` -> ``☀️``)."""
    icon = raw.strip()
    if len(icon) == 1 and unicodedata.category(icon) == "So":
        cp = ord(icon)
        if cp < 0x1F000 or cp in _TEXT_DEFAULT_SMP:
            icon += VS16
    return icon


def _check_icon(icon: str, *, allow_empty: bool) -> str:
    icon = normalise_icon(icon)
    if not icon:
        if allow_empty:
            return ""
        raise TagValidationError("icon may not be empty")
    if len(icon) > MAX_ICON_LEN:
        raise TagValidationError(f"icon longer than {MAX_ICON_LEN} characters")
    if any(ch.isspace() or unicodedata.category(ch) == "Cc" for ch in icon):
        raise TagValidationError("icon may not contain whitespace or control characters")
    return icon


def validate_icon_rules(rules: Sequence[IconRule]) -> tuple[IconRule, ...]:
    if len(rules) > MAX_ICON_RULES:
        raise TagValidationError(f"at most {MAX_ICON_RULES} icon rules are allowed")
    out: list[IconRule] = []
    seen: set[str] = set()
    for rule in rules:
        keyword = " ".join(rule.keyword.split())
        if not keyword:
            raise TagValidationError("icon keyword may not be empty")
        if len(keyword) > MAX_ICON_KEYWORD:
            raise TagValidationError(f"icon keyword longer than {MAX_ICON_KEYWORD} characters")
        key = keyword.casefold()
        if key in seen:
            raise TagValidationError(f"duplicate icon keyword: {keyword}")
        seen.add(key)
        out.append(IconRule(keyword, _check_icon(rule.icon, allow_empty=False)))
    return tuple(out)


def validate_fallback_icon(icon: str) -> str:
    return _check_icon(icon, allow_empty=True)


def icon_rules_from_json(data: Any) -> tuple[IconRule, ...]:
    if not isinstance(data, list):
        raise TagValidationError("iconRules must be a list")
    rules: list[IconRule] = []
    for item in data:
        if not isinstance(item, Mapping):
            raise TagValidationError("icon rule must be an object")
        rules.append(IconRule(str(item.get("keyword", "")), str(item.get("icon", ""))))
    return tuple(rules)


def icon_rules_to_json(rules: Iterable[IconRule]) -> list[dict[str, str]]:
    return [r.to_json() for r in rules]


def title_icon(summary: str, rules: Sequence[IconRule], fallback: str) -> str | None:
    """Icon of the first rule whose keyword occurs in ``summary``, else the fallback."""
    haystack = summary.casefold()
    for rule in rules:
        if rule.keyword.casefold() in haystack:
            return rule.icon
    return fallback or None


def _starts_with_icon(text: str) -> bool:
    return bool(text) and unicodedata.category(text[0]) == "So"


def with_icon(icon: str, text: str) -> str:
    return f"{icon} {text.lstrip()}"


def summary_icon(summary: str, rules: Sequence[IconRule], fallback: str) -> str | None:
    """Icon to put before ``summary``, or None when it already starts with one."""
    if _starts_with_icon(summary.lstrip()):
        return None
    return title_icon(summary, rules, fallback)


def prefix_summary(summary: str, rules: Sequence[IconRule], fallback: str) -> str:
    icon = summary_icon(summary, rules, fallback)
    return with_icon(icon, summary) if icon else summary


def decorate_description(description: str) -> str:
    """Prefix known ``Label:`` lines with their icon; leave everything else untouched."""
    out: list[str] = []
    for line in description.split("\n"):
        stripped = line.lstrip()
        label, sep, _ = stripped.partition(":")
        icon = LABEL_ICONS.get(label.strip().casefold()) if sep else None
        if icon and not _starts_with_icon(stripped):
            line = with_icon(icon, stripped)
        out.append(line)
    return "\n".join(out)
