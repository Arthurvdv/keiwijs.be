"""Byte-for-byte comparison of the rendered L3 feed against a reviewed golden file."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from make_golden import build  # noqa: E402

GOLDEN = ROOT / "tests" / "golden" / "l3.ics"


def test_l3_matches_golden() -> None:
    actual = build()
    expected = GOLDEN.read_bytes()
    if actual != expected:
        a = actual.decode("utf-8").splitlines()
        b = expected.decode("utf-8").splitlines()
        first = next(
            (i for i, (x, y) in enumerate(zip(a, b, strict=False)) if x != y), min(len(a), len(b))
        )
        raise AssertionError(
            f"rendered output differs from golden at line {first + 1}:\n"
            f"  actual:   {a[first] if first < len(a) else '<eof>'!r}\n"
            f"  expected: {b[first] if first < len(b) else '<eof>'!r}\n"
            "If the change is intended, run: python tools/make_golden.py"
        )


def test_golden_sanity() -> None:
    data = GOLDEN.read_bytes()
    assert data.count(b"BEGIN:VEVENT") == 64
    assert b"Extra deelnemers" not in data
    assert b"X-WR-CALNAME:GMail (L3)" in data
    assert "SUMMARY:☀️ Kerstvakantie".encode() in data
    assert "SUMMARY:📚 L3: Bib".encode() in data
    assert "DESCRIPTION:🗓️ Kalender: ".encode() in data
    assert all(len(line) <= 75 for line in data.split(b"\r\n"))
