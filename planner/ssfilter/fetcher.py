"""Upstream fetch with an SSRF guard: only SmartSchool planner feed URLs, public IPs only."""

from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from .config import DEFAULT_HOST_PATTERN, DEFAULT_PATH_PATTERN

MAX_URL_LEN = 1024
MAX_BODY_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 3
TIMEOUT = httpx.Timeout(15.0, connect=5.0)

ErrorKind = Literal[
    "invalid_url",
    "blocked",
    "dns",
    "timeout",
    "network",
    "http_status",
    "too_large",
    "not_ics",
    "redirect",
]


class UpstreamError(Exception):
    def __init__(self, kind: ErrorKind, message: str = ""):
        super().__init__(message or kind)
        self.kind: ErrorKind = kind


@dataclass(frozen=True)
class Upstream:
    body: bytes
    status: int
    final_url: str


_default_host = re.compile(DEFAULT_HOST_PATTERN)
_default_path = re.compile(DEFAULT_PATH_PATTERN)


def normalise_url(
    url: str,
    host_pattern: re.Pattern[str] = _default_host,
    path_pattern: re.Pattern[str] = _default_path,
) -> str:
    """Validate against the allowlist and return the canonical form used for hashing."""
    url = url.strip()
    if not url or len(url) > MAX_URL_LEN:
        raise UpstreamError("invalid_url", "url missing or too long")
    try:
        parts = urlsplit(url)
    except ValueError as exc:
        raise UpstreamError("invalid_url", "unparseable url") from exc
    if parts.scheme.lower() != "https":
        raise UpstreamError("invalid_url", "only https is allowed")
    if parts.username or parts.password:
        raise UpstreamError("invalid_url", "userinfo not allowed")
    host = (parts.hostname or "").lower()
    if not host or parts.port not in (None, 443):
        raise UpstreamError("invalid_url", "unexpected host or port")
    if not host_pattern.match(host):
        raise UpstreamError("blocked", "host not allowed")
    path = parts.path.rstrip("/") or "/"
    if not path_pattern.match(path):
        raise UpstreamError("blocked", "path not allowed")
    return urlunsplit(("https", host, path, "", ""))


def is_public_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


async def assert_public_host(host: str) -> None:
    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UpstreamError("dns", f"cannot resolve {host}") from exc
    addresses = {str(info[4][0]) for info in infos}
    if not addresses:
        raise UpstreamError("dns", f"no addresses for {host}")
    if not all(is_public_ip(a) for a in addresses):
        raise UpstreamError("blocked", "host resolves to a non-public address")


async def fetch_ics(
    url: str,
    client: httpx.AsyncClient,
    *,
    user_agent: str = "KeiwijsPlanner/1.0",
    host_pattern: re.Pattern[str] = _default_host,
    path_pattern: re.Pattern[str] = _default_path,
    max_bytes: int = MAX_BODY_BYTES,
) -> Upstream:
    """GET the feed, re-validating every redirect hop against the allowlist."""
    current = url
    for _hop in range(MAX_REDIRECTS + 1):
        current = normalise_url(current, host_pattern, path_pattern)
        await assert_public_host(urlsplit(current).hostname or "")
        headers = {"User-Agent": user_agent, "Accept": "text/calendar, text/plain;q=0.5, */*;q=0.1"}
        try:
            async with client.stream(
                "GET", current, headers=headers, follow_redirects=False, timeout=TIMEOUT
            ) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        raise UpstreamError("redirect", "redirect without location")
                    current = urljoin(current, location)
                    continue
                if response.status_code != 200:
                    raise UpstreamError("http_status", f"upstream returned {response.status_code}")
                chunks: list[bytes] = []
                size = 0
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    if size > max_bytes:
                        raise UpstreamError("too_large", "feed larger than limit")
                    chunks.append(chunk)
        except httpx.TimeoutException as exc:
            raise UpstreamError("timeout", "upstream timed out") from exc
        except httpx.HTTPError as exc:
            raise UpstreamError("network", f"network error: {exc.__class__.__name__}") from exc
        body = b"".join(chunks)
        if not body.lstrip(b"\xef\xbb\xbf").lstrip().upper().startswith(b"BEGIN:VCALENDAR"):
            raise UpstreamError("not_ics", "response is not an iCalendar stream")
        return Upstream(body, 200, current)
    raise UpstreamError("redirect", "too many redirects")


def new_client() -> httpx.AsyncClient:
    """Shared client: no proxies from the environment, sane limits, HTTP/1.1."""
    return httpx.AsyncClient(
        trust_env=False,
        timeout=TIMEOUT,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    )
