from __future__ import annotations

import pytest

from ssfilter.icons import (
    DEFAULT_ICON_RULES,
    MAX_ICON_RULES,
    IconRule,
    decorate_description,
    normalise_icon,
    prefix_summary,
    title_icon,
    validate_fallback_icon,
    validate_icon_rules,
)
from ssfilter.tags import TagValidationError

SUN = "☀️"


def test_first_match_wins_case_insensitive() -> None:
    rules = (IconRule("bib", "📚"), IconRule("L3", "🔢"))
    assert title_icon("L3: BIB", rules, "📌") == "📚"
    assert title_icon("L3 zwemmen", rules, "📌") == "🔢"


def test_fallback_when_nothing_matches() -> None:
    assert title_icon("Paaslunch", DEFAULT_ICON_RULES, "📌") == "📌"
    assert title_icon("Paaslunch", DEFAULT_ICON_RULES, "") is None
    assert prefix_summary("Paaslunch", DEFAULT_ICON_RULES, "") == "Paaslunch"


def test_prefix_uses_exactly_one_space() -> None:
    assert prefix_summary("Kerstvakantie", DEFAULT_ICON_RULES, "📌") == f"{SUN} Kerstvakantie"
    assert prefix_summary("  Kerstvakantie", DEFAULT_ICON_RULES, "📌") == f"{SUN} Kerstvakantie"


def test_prefix_is_idempotent() -> None:
    once = prefix_summary("L3: Bib", DEFAULT_ICON_RULES, "📌")
    assert once == "📚 L3: Bib"
    assert prefix_summary(once, DEFAULT_ICON_RULES, "📌") == once


def test_normalise_icon_adds_vs16_to_text_symbols() -> None:
    assert normalise_icon(" ☀ ") == SUN
    assert normalise_icon("🗓") == "🗓️"
    assert normalise_icon(SUN) == SUN
    assert normalise_icon("📚") == "📚"


def test_decorate_description_only_known_labels() -> None:
    text = (
        "Kalender: School\nOrganisator: A\nWeblink: Info (https://x)\n"
        "Organisatie of verloop:\nOm 8: verzamelen\nVoor de kleuters: niets"
    )
    assert decorate_description(text) == (
        "🗓️ Kalender: School\n👤 Organisator: A\n🔗 Weblink: Info (https://x)\n"
        "📝 Organisatie of verloop:\nOm 8: verzamelen\nVoor de kleuters: niets"
    )
    assert decorate_description(decorate_description(text)) == decorate_description(text)


def test_decorate_description_participants() -> None:
    assert decorate_description("Deelnemers: Iedereen") == "👥 Deelnemers: Iedereen"
    assert decorate_description("Extra deelnemers: ? A") == "👥 Extra deelnemers: ? A"


def test_decorate_description_drops_redundant_labels() -> None:
    text = (
        "Kalender: School\nOrganisator: A\nWeblink: Info (https://x)\n"
        "Deelnemers: Iedereen\nExtra deelnemers: ? A\nOrganisatie of verloop:\nOm 8: verzamelen"
    )
    once = decorate_description(text, drop_labels=True)
    assert once == (
        "🗓️ School\n👤 A\n🔗 Info (https://x)\n"
        "👥 Deelnemers: Iedereen\n👥 Extra deelnemers: ? A\n📝 Organisatie of verloop:\n"
        "Om 8: verzamelen"
    )
    assert decorate_description(once, drop_labels=True) == once
    assert decorate_description("Weblink:  ", drop_labels=True) == "🔗 Weblink:  "


def test_validate_icon_rules() -> None:
    assert validate_icon_rules([IconRule("  geen   school ", "☀")]) == (
        IconRule("geen school", SUN),
    )
    for bad in (
        [IconRule("", "📚")],
        [IconRule("bib", "")],
        [IconRule("bib", "a b")],
        [IconRule("x" * 41, "📚")],
        [IconRule("bib", "x" * 17)],
        [IconRule("bib", "📚"), IconRule("BIB", "📖")],
        [IconRule(f"k{i}", "📚") for i in range(MAX_ICON_RULES + 1)],
    ):
        with pytest.raises(TagValidationError):
            validate_icon_rules(bad)


def test_validate_fallback_icon() -> None:
    assert validate_fallback_icon("  ") == ""
    assert validate_fallback_icon("📌") == "📌"
    with pytest.raises(TagValidationError):
        validate_fallback_icon("a\tb")
