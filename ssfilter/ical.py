"""Minimal, byte-faithful iCalendar (RFC 5545) line processing.

Why hand-rolled: libraries such as ``icalendar`` or ``ics`` re-serialise and
normalise properties, which can drop or rewrite ``X-`` properties and change
folding. This module keeps every property we do not touch verbatim, which is
what calendar clients tracking UIDs across refreshes need.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

CRLF = "\r\n"
FOLD_LIMIT = 75  # octets per physical line, including the leading space on continuations

_LINE_SPLIT = re.compile(r"\r\n|\n|\r")


class IcsParseError(ValueError):
    """Raised when the input is not a usable iCalendar stream."""


@dataclass(frozen=True)
class ContentLine:
    """One unfolded logical line: ``NAME;PARAM=VALUE:value``."""

    name: str
    raw: str
    value: str
    params: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    def with_value(self, value: str) -> ContentLine:
        """Return a copy with a new (already escaped) value, parameters preserved."""
        head = self.raw[: len(self.raw) - len(self.value)]
        return ContentLine(self.name, head + value, value, self.params)


@dataclass
class Component:
    name: str
    props: list[ContentLine] = field(default_factory=list)
    children: list[Component] = field(default_factory=list)

    def get(self, name: str) -> ContentLine | None:
        upper = name.upper()
        for prop in self.props:
            if prop.name == upper:
                return prop
        return None

    def set(self, line: ContentLine) -> None:
        """Replace the first property with the same name, or append."""
        for idx, prop in enumerate(self.props):
            if prop.name == line.name:
                self.props[idx] = line
                return
        self.props.append(line)

    def remove(self, name: str) -> None:
        upper = name.upper()
        self.props = [p for p in self.props if p.name != upper]

    def events(self) -> Iterable[Component]:
        return (c for c in self.children if c.name == "VEVENT")

    def clone(self) -> Component:
        """Structural copy; ContentLine objects are immutable and shared."""
        return Component(self.name, list(self.props), [c.clone() for c in self.children])


# --------------------------------------------------------------------------- lines


def unfold(data: bytes) -> list[str]:
    """Decode UTF-8 (BOM tolerated), split on any newline style and unfold continuations."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise IcsParseError("feed is not valid UTF-8") from exc
    lines: list[str] = []
    for physical in _LINE_SPLIT.split(text):
        if physical[:1] in (" ", "\t") and lines:
            lines[-1] += physical[1:]
        elif physical:
            lines.append(physical)
    return lines


def fold(line: str, limit: int = FOLD_LIMIT) -> list[str]:
    """Split a logical line into physical lines of at most ``limit`` octets.

    Continuation lines start with a single space that counts toward the limit.
    Multi-byte UTF-8 sequences are never split.
    """
    if limit < 8:
        raise ValueError("fold limit too small")
    out: list[str] = []
    current: list[str] = []
    used = 0
    for ch in line:
        size = len(ch.encode("utf-8"))
        if used + size > limit:
            out.append("".join(current))
            current = [" ", ch]
            used = 1 + size
        else:
            current.append(ch)
            used += size
    out.append("".join(current))
    return out


def parse_line(raw: str) -> ContentLine:
    """Split ``NAME;P=V;Q="a:b":value`` respecting quoted parameter values."""
    in_quotes = False
    colon = -1
    for idx, ch in enumerate(raw):
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ":" and not in_quotes:
            colon = idx
            break
    if colon <= 0:
        raise IcsParseError(f"content line without ':' separator: {raw[:40]!r}")
    head, value = raw[:colon], raw[colon + 1 :]
    parts = _split_unquoted(head, ";")
    name = parts[0].strip().upper()
    if not name:
        raise IcsParseError("content line without a property name")
    params: dict[str, str] = {}
    for part in parts[1:]:
        if "=" in part:
            key, val = part.split("=", 1)
            params[key.strip().upper()] = val.strip().strip('"')
        elif part:
            params[part.strip().upper()] = ""
    return ContentLine(name, raw, value, MappingProxyType(params))


def _split_unquoted(text: str, sep: str) -> list[str]:
    out: list[str] = []
    buf: list[str] = []
    in_quotes = False
    for ch in text:
        if ch == '"':
            in_quotes = not in_quotes
            buf.append(ch)
        elif ch == sep and not in_quotes:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out


def make_line(name: str, value: str, params: Mapping[str, str] | None = None) -> ContentLine:
    """Build a content line from parts. ``value`` must already be escaped."""
    head = name.upper()
    for key, val in (params or {}).items():
        head += f";{key.upper()}={val}"
    return ContentLine(name.upper(), f"{head}:{value}", value, MappingProxyType(dict(params or {})))


# --------------------------------------------------------------------------- components


def parse(data: bytes) -> Component:
    """Parse the stream into a tree; the root is the (single) VCALENDAR."""
    root = Component("__ROOT__")
    stack: list[Component] = [root]
    for raw in unfold(data):
        line = parse_line(raw)
        if line.name == "BEGIN":
            child = Component(line.value.strip().upper())
            stack[-1].children.append(child)
            stack.append(child)
        elif line.name == "END":
            if len(stack) == 1:
                raise IcsParseError("END without matching BEGIN")
            closing = stack.pop()
            if closing.name != line.value.strip().upper():
                raise IcsParseError(f"END:{line.value} closes {closing.name}")
        else:
            stack[-1].props.append(line)
    if len(stack) != 1:
        raise IcsParseError(f"unterminated component {stack[-1].name}")
    calendars = [c for c in root.children if c.name == "VCALENDAR"]
    if len(calendars) != 1:
        raise IcsParseError(f"expected exactly one VCALENDAR, found {len(calendars)}")
    return calendars[0]


def serialize(component: Component) -> bytes:
    """Render with CRLF line endings and RFC 5545 folding."""
    out: list[str] = []
    _emit(component, out)
    return (CRLF.join(out) + CRLF).encode("utf-8")


def _emit(component: Component, out: list[str]) -> None:
    out.extend(fold(f"BEGIN:{component.name}"))
    for prop in component.props:
        out.extend(fold(prop.raw))
    for child in component.children:
        _emit(child, out)
    out.extend(fold(f"END:{component.name}"))


# --------------------------------------------------------------------------- text values


def unescape_text(value: str) -> str:
    out: list[str] = []
    i = 0
    n = len(value)
    while i < n:
        ch = value[i]
        if ch == "\\" and i + 1 < n:
            nxt = value[i + 1]
            if nxt in "nN":
                out.append("\n")
            elif nxt in ",;\\":
                out.append(nxt)
            else:
                out.append(ch)
                out.append(nxt)
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def split_text_list(value: str) -> list[str]:
    """Split an escaped TEXT value on unescaped commas, returning unescaped items."""
    items: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(value)
    while i < n:
        ch = value[i]
        if ch == "\\" and i + 1 < n:
            buf.append(ch)
            buf.append(value[i + 1])
            i += 2
            continue
        if ch == ",":
            items.append(unescape_text("".join(buf)))
            buf = []
        else:
            buf.append(ch)
        i += 1
    items.append(unescape_text("".join(buf)))
    return items


def text_value(component: Component, name: str) -> str:
    """Unescaped value of a TEXT property, or ``""`` when absent."""
    prop = component.get(name)
    return unescape_text(prop.value) if prop else ""
