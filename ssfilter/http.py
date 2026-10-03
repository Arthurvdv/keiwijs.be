"""Small HTTP helpers for the Azure Functions handlers: JSON, CORS, rate limiting."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import azure.functions as func

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "X-Robots-Tag": "noindex",
}


def cors_headers(req: func.HttpRequest, allowed_origins: tuple[str, ...]) -> dict[str, str]:
    origin = req.headers.get("Origin", "")
    if origin and origin.rstrip("/") in allowed_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "600",
            "Vary": "Origin",
        }
    return {"Vary": "Origin"}


def json_response(
    data: Any, status: int = 200, headers: Mapping[str, str] | None = None
) -> func.HttpResponse:
    merged = {**SECURITY_HEADERS, **(headers or {})}
    return func.HttpResponse(
        json.dumps(data, ensure_ascii=False),
        status_code=status,
        mimetype="application/json",
        charset="utf-8",
        headers=merged,
    )


def error_response(
    status: int, code: str, message: str, headers: Mapping[str, str] | None = None
) -> func.HttpResponse:
    return json_response({"error": code, "message": message}, status, headers)


def read_json(req: func.HttpRequest) -> dict[str, Any]:
    body = req.get_body()
    if len(body) > 64 * 1024:
        raise ValueError("request body too large")
    if not body:
        return {}
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON object expected")
    return data


def client_ip(req: func.HttpRequest) -> str:
    forwarded = req.headers.get("X-Forwarded-For", "")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        # Azure appends the port for IPv4 ("1.2.3.4:5678"); IPv6 arrives bracketed.
        if first.count(":") == 1 and not first.startswith("["):
            first = first.split(":")[0]
        return str(first.strip("[]"))
    return str(req.headers.get("X-Client-IP", "unknown"))


@dataclass
class RateLimiter:
    """Token bucket per key; best-effort, in-process only."""

    rate_per_minute: float = 30.0
    burst: int = 15
    _buckets: dict[str, tuple[float, float]] = field(default_factory=dict)

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        tokens, last = self._buckets.get(key, (float(self.burst), now))
        tokens = min(float(self.burst), tokens + (now - last) * self.rate_per_minute / 60.0)
        if tokens < 1.0:
            self._buckets[key] = (tokens, now)
            return False
        self._buckets[key] = (tokens - 1.0, now)
        if len(self._buckets) > 10_000:
            self._buckets.clear()
        return True
