from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ssfilter import ical

_line_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="\r\n"),
    min_size=1,
    max_size=400,
).filter(lambda s: s[0] not in " \t")


@given(_line_text)
def test_fold_unfold_round_trip(line: str) -> None:
    physical = ical.fold(line)
    assert all(len(p.encode("utf-8")) <= ical.FOLD_LIMIT for p in physical)
    joined = "\r\n".join(physical).encode("utf-8")
    assert ical.unfold(joined) == [line]


def test_fold_never_splits_utf8() -> None:
    line = "DESCRIPTION:" + "coördinator ✓ Amélie " * 10
    for part in ical.fold(line):
        part.encode("utf-8")  # would raise on a lone surrogate
        assert len(part.encode("utf-8")) <= 75


def test_parse_line_with_quoted_param() -> None:
    cl = ical.parse_line('ATTENDEE;CN="Doe, John: x";ROLE=REQ:mailto:j@example.org')
    assert cl.name == "ATTENDEE"
    assert cl.params["CN"] == "Doe, John: x"
    assert cl.params["ROLE"] == "REQ"
    assert cl.value == "mailto:j@example.org"


def test_parse_line_without_colon_raises() -> None:
    with pytest.raises(ical.IcsParseError):
        ical.parse_line("NOCOLONHERE")


def test_fixture_round_trip_is_stable(fixture_bytes: bytes) -> None:
    cal = ical.parse(fixture_bytes)
    once = ical.serialize(cal)
    twice = ical.serialize(ical.parse(once))
    assert once == twice
    assert once.endswith(b"\r\n")
    assert b"\n" not in once.replace(b"\r\n", b"")
    for physical in once.split(b"\r\n"):
        assert len(physical) <= 75


def test_fixture_structure(calendar: ical.Component) -> None:
    assert calendar.name == "VCALENDAR"
    events = list(calendar.events())
    assert len(events) == 90
    assert ical.text_value(calendar, "X-WR-TIMEZONE") == "Europe/Brussels"
    assert calendar.get("REFRESH-INTERVAL") is not None
    uids = {ical.text_value(e, "UID") for e in events}
    assert len(uids) == 90


def test_unknown_properties_survive_verbatim() -> None:
    src = (
        b"BEGIN:VCALENDAR\r\nX-FOO;BAR=1:keep me\r\nBEGIN:VEVENT\r\nUID:1\r\n"
        b'X-WEIRD;A="b;c":v\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'
    )
    out = ical.serialize(ical.parse(src))
    assert out == src


def test_escape_unescape_round_trip() -> None:
    text = "a,b;c\\d\nnew line"
    assert ical.unescape_text(ical.escape_text(text)) == text


def test_split_text_list_respects_escapes() -> None:
    assert ical.split_text_list("Jan\\, L3 Jan,Piet\\, L6 Piet") == ["Jan, L3 Jan", "Piet, L6 Piet"]


def test_set_replaces_first_and_appends() -> None:
    comp = ical.Component("VEVENT", [ical.make_line("SUMMARY", "a")])
    comp.set(ical.make_line("SUMMARY", "b"))
    comp.set(ical.make_line("X-NEW", "c"))
    assert [p.raw for p in comp.props] == ["SUMMARY:b", "X-NEW:c"]


def test_parse_rejects_unbalanced() -> None:
    with pytest.raises(ical.IcsParseError):
        ical.parse(b"BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nEND:VCALENDAR\r\n")
    with pytest.raises(ical.IcsParseError):
        ical.parse(b"X:y\r\n")
