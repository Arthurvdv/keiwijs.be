from __future__ import annotations

from pathlib import Path

import pytest

from ssfilter import ical

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixture_bytes() -> bytes:
    return (FIXTURES / "calendar_anon.ics").read_bytes()


@pytest.fixture()
def calendar(fixture_bytes: bytes) -> ical.Component:
    return ical.parse(fixture_bytes)
