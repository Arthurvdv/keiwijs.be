"""Regenerate tests/golden/l3.ics from the anonymised fixture (L3 selected, defaults otherwise).

Run after an intentional change to the output format and review the diff before committing.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ssfilter import ical  # noqa: E402
from ssfilter.rules import FilterConfig, RuleEngine  # noqa: E402
from ssfilter.tags import Tag, default_tags  # noqa: E402
from ssfilter.transform import render  # noqa: E402


def golden_config() -> FilterConfig:
    tags = tuple(Tag(t.name, t.name == "L3", t.name == "L3") for t in default_tags())
    return FilterConfig(tags=tags)


def build() -> bytes:
    calendar = ical.parse((ROOT / "tests" / "fixtures" / "calendar_anon.ics").read_bytes())
    cfg = golden_config()
    filtered, _ = RuleEngine(cfg).apply(calendar)
    return render(filtered, cfg)


if __name__ == "__main__":
    target = ROOT / "tests" / "golden" / "l3.ics"
    target.write_bytes(build())
    print(f"wrote {target} ({target.stat().st_size} bytes)")
