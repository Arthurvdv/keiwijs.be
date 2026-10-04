"""Replace teacher and pupil names in a SmartSchool Planner ICS with deterministic fakes.

Usage: python tools/anonymise_ics.py <input.ics> <output.ics>

Names are found in the ``Organisator:`` and ``Extra deelnemers:`` lines of
DESCRIPTION. Teachers look like ``First Last ROLE Last``; pupils like ``? First Last``.
The same real name always maps to the same fake name within one run, and the
structure (roles, markers, folding) is preserved so tests exercise real shapes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ssfilter import ical  # noqa: E402

FAKE_TEACHERS = [
    ("An", "Peeters"),
    ("Bart", "Janssens"),
    ("Carla", "Maes"),
    ("Dirk", "Jacobs"),
    ("Els", "Mertens"),
    ("Frank", "Willems"),
    ("Greet", "Claes"),
    ("Hans", "Goossens"),
    ("Ilse", "Wouters"),
    ("Jan", "De Smet"),
    ("Katrien", "Dubois"),
    ("Lies", "Vermeulen"),
]
ROLE = r"(?:[KL][1-6]|Zorgleerkracht|Zorgco(?:ö|o)rdinator|Directie|Directeur|Leerkracht|Secretariaat|ICT)"  # noqa: E501
TEACHER_RE = re.compile(rf"^(?P<mark>[✓?]\s*)?(?P<full>.+?)\s+(?P<role>{ROLE})\s+(?P<last>.+)$")
PUPIL_RE = re.compile(r"^(?P<mark>[✓?]\s*)(?P<full>.+)$")
SCHOOL_RE = re.compile(r"Kalender: .+? voor ouders")


class Anonymiser:
    def __init__(self) -> None:
        self.teachers: dict[str, tuple[str, str]] = {}
        self.pupils: dict[str, str] = {}
        self.real_tokens: set[str] = set()

    def teacher(self, full: str) -> tuple[str, str]:
        if full not in self.teachers:
            self.teachers[full] = FAKE_TEACHERS[len(self.teachers) % len(FAKE_TEACHERS)]
            self.real_tokens.update(t for t in full.split() if len(t) > 2)
        return self.teachers[full]

    def pupil(self, full: str) -> str:
        if full not in self.pupils:
            self.pupils[full] = f"Leerling {len(self.pupils) + 1:02d}"
            self.real_tokens.update(t for t in full.split() if len(t) > 2)
        return self.pupils[full]

    def entry(self, text: str) -> str:
        m = TEACHER_RE.match(text)
        if m:
            first, last = self.teacher(m.group("full"))
            return f"{m.group('mark') or ''}{first} {last} {m.group('role')} {last}"
        m = PUPIL_RE.match(text)
        if m:
            return f"{m.group('mark')}{self.pupil(m.group('full'))}"
        return text

    def description(self, value: str) -> str:
        lines = ical.unescape_text(value).split("\n")
        out: list[str] = []
        for line in lines:
            key, sep, rest = line.partition(":")
            if sep and key.strip() in ("Organisator", "Extra deelnemers"):
                entries = [e.strip() for e in rest.split(",")]
                rest = ", ".join(self.entry(e) for e in entries if e) if rest.strip() else rest
                out.append(f"{key}:{(' ' + rest) if rest.strip() else rest}")
            else:
                out.append(line)
        text = "\n".join(out)
        text = SCHOOL_RE.sub("Kalender: Voorbeeldschool voor ouders", text)
        return ical.escape_text(text)


def main(src: Path, dst: Path) -> None:
    cal = ical.parse(src.read_bytes())
    anon = Anonymiser()
    for ev in cal.events():
        prop = ev.get("DESCRIPTION")
        if prop:
            ev.set(prop.with_value(anon.description(prop.value)))
    data = ical.serialize(cal)
    leaked = sorted(t for t in anon.real_tokens if t.encode() in data)
    if leaked:
        raise SystemExit(f"real name tokens still present: {leaked}")
    dst.write_bytes(data)
    print(f"teachers={len(anon.teachers)} pupils={len(anon.pupils)} bytes={len(data)} -> {dst}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
