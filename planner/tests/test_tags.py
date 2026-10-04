from __future__ import annotations

from datetime import UTC, datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ssfilter import tags as tg

DEFAULT = tg.default_tags()
MATCHER = tg.TagMatcher(DEFAULT)


@pytest.mark.parametrize(
    ("summary", "expected", "all_hit"),
    [
        ("L3: Bib", {"L3"}, False),
        ("L2: Bib", {"L2"}, False),
        ("L4 + L6 bib", {"L4", "L6"}, False),
        ("Vaccinaties in L2 en L4", {"L2", "L4"}, False),
        ("Vaccinaties L1", {"L1"}, False),
        ("L6 Vlaamse toets 1", {"L6"}, False),
        ("Vlaamse toets L4", {"L4"}, False),
        ("Vlaamse toetsen 2", set(), False),
        ("Boostersessie CLB voor L6", {"L6"}, False),
        ("Oudercontacten lagere school (L1-L6)", {"L1", "L2", "L3", "L4", "L5", "L6"}, False),
        ("Oudercontact kleuters + L6", {"K1", "K2", "K3", "L6"}, False),
        ("Oudercontact iedereen (behalve instapklas)", set(), True),
        ("Oudercontact instapklas", set(), False),
        ("Rapport 1 lagere school", {"L1", "L2", "L3", "L4", "L5", "L6"}, False),
        ("Zwemmen", set(), False),
        ("Pedagogische studiedag: geen school!", set(), False),
        ("Sinterklaas", set(), False),
        ("Proclamatie L6", {"L6"}, False),
        ("Zeeklassen", set(), False),
        ("Infoavond derde leerjaar", {"L3"}, False),
        ("Uitstap 2de kleuterklas", {"K2"}, False),
        ("Workshop L1-L3", {"L1", "L2", "L3"}, False),
        ("Bosklassen L5 t/m L6", {"L5", "L6"}, False),
        ("Bib L3 om 13u30", {"L3"}, False),
        ("Sportdag iedereen behalve L6", {"K1", "K2", "K3", "L1", "L2", "L3", "L4", "L5"}, False),
        ("Rondleiding ouders 2027", set(), False),
    ],
)
def test_summary_matching(summary: str, expected: set[str], all_hit: bool) -> None:
    sig = MATCHER.match(summary)
    assert set(sig.matched) == expected
    assert sig.all_hit is all_hit


def test_lagere_school_maps_to_all_l_tags_when_k_tags_absent() -> None:
    only_lager = tg.TagMatcher([tg.Tag(n) for n in ("L1", "L2", "L3")])
    sig = only_lager.match("Rapport lagere school")
    assert sig.matched == frozenset() and sig.all_hit  # all tags matched => treated as untagged


def test_custom_tag_literal_match() -> None:
    matcher = tg.TagMatcher([tg.Tag("Instapklas"), tg.Tag("K1"), tg.Tag("Peuters")])
    assert set(matcher.match("Oudercontact instapklas").matched) == {"Instapklas"}
    assert set(matcher.match("Oudercontact iedereen (behalve instapklas)").matched) == {
        "K1",
        "Peuters",
    }
    assert matcher.match("Instapklassen").matched == frozenset()  # word boundary


def test_organisator_fallback_opt_in() -> None:
    desc = "Kalender: X\nOrganisator: An Peeters L2 Peeters"
    assert MATCHER.match("Bib", desc).matched == frozenset()
    sig = MATCHER.match("Bib", desc, use_organisator=True)
    assert set(sig.matched) == {"L2"} and sig.source == "organisator"


def test_organisator_fallback_ignored_when_ambiguous() -> None:
    desc = "Organisator: A L6 A, B L2 B, C Zorgcoördinator C"
    sig = MATCHER.match("Zwemmen", desc, use_organisator=True)
    assert sig.matched == frozenset() and sig.source == "none"


def test_description_body_does_not_drive_matching() -> None:
    desc = "Organisatie of verloop:\ngeen zwemmen voor L6"
    assert MATCHER.match("Zwemmen", desc, use_organisator=True).matched == frozenset()


# --------------------------------------------------------------------------- rollover


def _tags(spec: str) -> list[tg.Tag]:
    """'K1 K2* K3+ L1' -> * selected+move, + selected only."""
    out = []
    for token in spec.split():
        name = token.rstrip("*+")
        out.append(tg.Tag(name, token.endswith(("*", "+")), token.endswith("*")))
    return out


def _spec(tags: list[tg.Tag]) -> str:
    return " ".join(t.name + ("*" if t.move_next else "+" if t.selected else "") for t in tags)


@pytest.mark.parametrize(
    ("before", "after", "moved", "dropped"),
    [
        ("K1 K2* K3 L1 L2 L3 L4* L5 L6", "K1 K2 K3* L1 L2 L3 L4 L5* L6", 2, 0),
        ("K1 K2 K3* L1 L2 L3 L4 L5 L6", "K1 K2 K3 L1* L2 L3 L4 L5 L6", 1, 0),
        ("K1 K2 K3 L1 L2 L3 L4 L5 L6*", "K1 K2 K3 L1 L2 L3 L4 L5 L6", 0, 1),
        ("K1 K2+ K3 L1 L2 L3 L4 L5 L6", "K1 K2+ K3 L1 L2 L3 L4 L5 L6", 0, 0),
        ("K1 K2* K3+ L1", "K1 K2 K3* L1", 1, 0),
        ("Peuters* K1 K2 K3", "Peuters K1* K2 K3", 1, 0),
        ("K1 K2 K3", "K1 K2 K3", 0, 0),
    ],
)
def test_rollover(before: str, after: str, moved: int, dropped: int) -> None:
    new, report = tg.rollover(_tags(before))
    assert _spec(new) == after
    assert len(report.moved) == moved
    assert len(report.dropped_at_end) == dropped


_tag_lists = st.lists(
    st.builds(tg.Tag, st.text(min_size=1, max_size=5), st.booleans(), st.booleans()),
    min_size=1,
    max_size=12,
)


@given(_tag_lists)
def test_rollover_invariants(tags: list[tg.Tag]) -> None:
    before = [t.normalised() for t in tags]
    new, report = tg.rollover(before)
    assert [t.name for t in new] == [t.name for t in before]
    assert all(t.selected or not t.move_next for t in new)
    assert sum(t.selected for t in new) <= sum(t.selected for t in before)
    assert len(report.moved) + len(report.kept) + len(report.dropped_at_end) == sum(
        t.selected for t in before
    )


# --------------------------------------------------------------------------- validation & dates


def test_validate_tags_rules() -> None:
    with pytest.raises(tg.TagValidationError):
        tg.validate_tags([])
    with pytest.raises(tg.TagValidationError):
        tg.validate_tags([tg.Tag("L1"), tg.Tag("l1")])
    with pytest.raises(tg.TagValidationError):
        tg.validate_tags([tg.Tag("  ")])
    norm = tg.validate_tags([tg.Tag("  L1   x ", False, True)])
    assert norm == [tg.Tag("L1 x", False, False)]


def test_validate_month_day() -> None:
    assert tg.validate_month_day("07-01") == "07-01"
    assert tg.validate_month_day("02-29") == "02-29"
    for bad in ("7-1", "13-01", "02-30", "2026-07-01", ""):
        with pytest.raises(tg.TagValidationError):
            tg.validate_month_day(bad)


def test_next_rollover_utc() -> None:
    after = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
    nxt = tg.next_rollover_utc("07-01", after)
    assert nxt == datetime(2027, 7, 1, 1, 0, tzinfo=UTC)  # 03:00 CEST
    # strictly after: a config saved on the rollover day at 02:00 UTC already passed 01:00 UTC
    assert tg.next_rollover_utc("07-01", datetime(2027, 7, 1, 2, 0, tzinfo=UTC)).year == 2028
    # Feb 29 falls back to Feb 28 in non-leap years
    assert tg.next_rollover_utc("02-29", datetime(2026, 3, 1, tzinfo=UTC)).day == 28
    with pytest.raises(ValueError, match="timezone-aware"):
        tg.next_rollover_utc("07-01", datetime(2026, 1, 1))


def test_tags_json_round_trip() -> None:
    tags = _tags("K1 K2* K3+")
    assert tg.tags_from_json(tg.tags_to_json(tags)) == tags
