from __future__ import annotations

from collections import Counter

import pytest

from ssfilter import ical
from ssfilter.rules import FilterConfig, RuleEngine, clean_keywords
from ssfilter.tags import Tag, default_tags
from ssfilter.transform import content_fingerprint, render, strip_extra_deelnemers


def _cfg(selected: set[str], **kw: object) -> FilterConfig:
    tags = tuple(Tag(t.name, t.name in selected, t.name in selected) for t in default_tags())
    return FilterConfig(tags=tags, **kw)  # type: ignore[arg-type]


def test_precedence_matrix() -> None:
    engine = RuleEngine(_cfg({"L3"}, include_keywords=("zwemmen",), exclude_keywords=("fluo",)))
    assert engine.decide("Start fluo-actie L3").reason == "exclude_kw"
    assert engine.decide("Zwemmen L6").reason == "include_kw"
    assert engine.decide("L3: Bib").reason == "tag_match"
    assert engine.decide("L2: Bib").reason == "tag_mismatch"
    assert engine.decide("Sinterklaas").reason == "untagged_kept"
    assert RuleEngine(_cfg({"L3"}, include_untagged=False)).decide("Sinterklaas").reason == (
        "untagged_dropped"
    )


def test_fixture_counts_for_l3(calendar: ical.Component) -> None:
    engine = RuleEngine(_cfg({"L3"}))
    filtered, decisions = engine.apply(calendar)
    reasons = Counter(d.reason for _, d in decisions)
    assert len(decisions) == 90
    assert reasons["tag_match"] == 16  # 8x "L3: Bib", fanfare, biebexpeditie, 6x "lagere school"
    assert reasons["tag_mismatch"] == 26
    assert reasons["untagged_kept"] == 48
    kept_uids = {ical.text_value(e, "UID") for e in filtered.events()}
    assert len(kept_uids) == 64
    assert all(d.keep for e, d in decisions if ical.text_value(e, "UID") in kept_uids)
    # original untouched
    assert len(list(calendar.events())) == 90


def test_fixture_counts_for_l3_without_untagged(calendar: ical.Component) -> None:
    engine = RuleEngine(_cfg({"L3"}, include_untagged=False))
    filtered, _ = engine.apply(calendar)
    assert len(list(filtered.events())) == 16


def test_two_children(calendar: ical.Component) -> None:
    engine = RuleEngine(_cfg({"L2", "L4"}, include_untagged=False))
    filtered, _ = engine.apply(calendar)
    summaries = sorted(ical.text_value(e, "SUMMARY") for e in filtered.events())
    assert "L2: Bib" in summaries and "L4 + L6 bib" in summaries
    assert "Vaccinaties in L2 en L4" in summaries
    assert not any(s.startswith("L3") for s in summaries)


def test_clean_keywords() -> None:
    assert clean_keywords([" Zwemmen ", "zwemmen", "", "x"]) == ("Zwemmen", "x")
    with pytest.raises(ValueError, match="at most"):
        clean_keywords([str(i) for i in range(21)])


def test_strip_extra_deelnemers() -> None:
    text = "Kalender: X\nExtra deelnemers: ? A, ? B\nOrganisator: C L2 C"
    assert strip_extra_deelnemers(text) == ("Kalender: X\nOrganisator: C L2 C", True)
    assert strip_extra_deelnemers("Kalender: X") == ("Kalender: X", False)


def test_participants_and_icons(calendar: ical.Component) -> None:
    stripped = render(RuleEngine(_cfg({"L4"})).apply(calendar)[0], _cfg({"L4"})).decode("utf-8")
    assert "Extra deelnemers" not in stripped
    cfg = _cfg({"L4"}, strip_participants=False, title_icons=False)
    kept = ical.parse(render(RuleEngine(cfg).apply(calendar)[0], cfg))
    toets = next(e for e in kept.events() if ical.text_value(e, "SUMMARY") == "Vlaamse toets L4")
    description = ical.text_value(toets, "DESCRIPTION")
    assert "👥 Extra deelnemers: " in description
    assert "🗓️ Kalender: " in description  # labels stay when title icons are off


def test_render_output_properties(calendar: ical.Component) -> None:
    cfg = _cfg({"L2"})
    filtered, _ = RuleEngine(cfg).apply(calendar)
    data = render(filtered, cfg)
    text = data.decode("utf-8")
    assert "Extra deelnemers" not in text
    assert "Leerling 01" not in text
    assert "X-WR-CALNAME:GMail (L2)" in text
    assert "REFRESH-INTERVAL;VALUE=DURATION:PT1H" in text
    assert "X-PUBLISHED-TTL:PT1H" in text
    assert "PRODID:-//Smartbit Bvba//Smartschool Calendar//BE" in text
    for physical in data.split(b"\r\n"):
        assert len(physical) <= 75
    # still parses and keeps UIDs from the source
    out = ical.parse(data)
    src_uids = {ical.text_value(e, "UID") for e in calendar.events()}
    assert {ical.text_value(e, "UID") for e in out.events()} <= src_uids


def test_render_validates_with_icalendar(calendar: ical.Component) -> None:
    icalendar = pytest.importorskip("icalendar")
    cfg = _cfg({"L3"})
    filtered, _ = RuleEngine(cfg).apply(calendar)
    parsed = icalendar.Calendar.from_ical(render(filtered, cfg))
    assert len(parsed.walk("VEVENT")) == 64


def test_fingerprint_ignores_dtstamp(fixture_bytes: bytes) -> None:
    a = content_fingerprint(fixture_bytes)
    b = content_fingerprint(
        fixture_bytes.replace(b"DTSTAMP:20261003T082130Z", b"DTSTAMP:20991231T000000Z")
    )
    c = content_fingerprint(fixture_bytes.replace(b"SUMMARY:Zwemmen", b"SUMMARY:Zwemmen!"))
    assert a == b
    assert a != c
