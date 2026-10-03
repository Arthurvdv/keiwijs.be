"""Azure Functions entry point (Python v2 programming model)."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

import azure.functions as func

from ssfilter.config import Settings
from ssfilter.http import (
    RateLimiter,
    client_ip,
    cors_headers,
    error_response,
    json_response,
    read_json,
)
from ssfilter.service import ApiError, App

log = logging.getLogger("ssfilter.function_app")
app = func.FunctionApp()

_settings: Settings | None = None
_app: App | None = None
_limiter = RateLimiter()


def settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def service() -> App:
    global _app
    if _app is None:
        _app = App.build(settings())
    return _app


Handler = Callable[[func.HttpRequest, App], Awaitable[func.HttpResponse]]


async def _api(
    req: func.HttpRequest, handler: Handler, *, limited: bool = True
) -> func.HttpResponse:
    headers = cors_headers(req, settings().allowed_origins)
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=headers)
    if limited and not _limiter.allow(client_ip(req)):
        return error_response(
            429, "rate_limited", "Te veel verzoeken, probeer zo meteen opnieuw.", headers
        )
    try:
        response = await handler(req, service())
    except ApiError as exc:
        return error_response(exc.status, exc.code, exc.message, headers)
    except ValueError as exc:
        return error_response(400, "bad_request", str(exc), headers)
    except Exception:  # noqa: BLE001
        log.exception("unhandled error in %s", req.url.split("?")[0].rsplit("/", 1)[-1])
        return error_response(500, "internal", "Onverwachte fout.", headers)
    for key, value in headers.items():
        response.headers[key] = value
    return response


# ----------------------------------------------------------------------------- API


@app.route(route="api/inspect", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
async def api_inspect(req: func.HttpRequest) -> func.HttpResponse:
    async def handler(r: func.HttpRequest, svc: App) -> func.HttpResponse:
        body = read_json(r)
        return json_response(await svc.inspect(body.get("url")))

    return await _api(req, handler)


@app.route(route="api/preview", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
async def api_preview(req: func.HttpRequest) -> func.HttpResponse:
    async def handler(r: func.HttpRequest, svc: App) -> func.HttpResponse:
        body = read_json(r)
        return json_response(await svc.preview(body.get("url"), body.get("settings")))

    return await _api(req, handler)


@app.route(
    route="api/config", methods=["POST", "DELETE", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS
)
async def api_config(req: func.HttpRequest) -> func.HttpResponse:
    async def handler(r: func.HttpRequest, svc: App) -> func.HttpResponse:
        body = read_json(r)
        if r.method == "DELETE":
            deleted = svc.delete(body.get("url"))
            return json_response({"deleted": deleted}, 200 if deleted else 404)
        settings_dto: Any = body.get("settings")
        if not isinstance(settings_dto, dict):
            raise ApiError(400, "invalid_settings", "settings object required")
        return json_response(await svc.save(body.get("url"), settings_dto))

    return await _api(req, handler)


@app.route(route="healthz", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def healthz(req: func.HttpRequest) -> func.HttpResponse:
    async def handler(_r: func.HttpRequest, svc: App) -> func.HttpResponse:
        return json_response(svc.health())

    return await _api(req, handler, limited=False)


# ----------------------------------------------------------------------------- ops (function key)


@app.route(route="ops/render", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
async def admin_render(req: func.HttpRequest) -> func.HttpResponse:
    row_key = req.params.get("rowKey")
    svc = service()
    if row_key:
        result = await svc.render_by_row_key(row_key)
        if result is None:
            return error_response(404, "not_found", "unknown rowKey")
        return json_response(
            {
                "ok": result.ok,
                "changed": result.changed,
                "eventCount": result.event_count,
                "error": result.error,
            }
        )
    summary = await svc.renderer.render_all()
    return json_response(summary.__dict__)


@app.route(route="ops/rollover", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
async def admin_rollover(req: func.HttpRequest) -> func.HttpResponse:
    """Dry-run or apply due rollovers without fetching upstream."""
    svc = service()
    dry_run = req.params.get("dryRun", "1") != "0"
    row_key = req.params.get("rowKey")
    configs = [c for c in ([svc.repo.get(row_key)] if row_key else svc.repo.list_all()) if c]
    now = svc.renderer.now()
    out: list[dict[str, object]] = []
    for cfg in configs:
        if cfg.next_rollover_utc > now:
            continue
        if dry_run:
            from ssfilter.tags import rollover

            _new, report = rollover(cfg.tags)
            out.append({"rowKey": cfg.row_key[:8], "wouldApply": report.summary()})
        else:
            reports = svc.renderer.apply_due_rollovers(cfg, trigger="admin")
            out.append({"rowKey": cfg.row_key[:8], "applied": [r.summary() for r in reports]})
    return json_response({"dryRun": dry_run, "count": len(out), "items": out})


# ----------------------------------------------------------------------------- timer


@app.timer_trigger(schedule="0 7 * * * *", arg_name="timer", run_on_startup=False)
async def render_all_hourly(timer: func.TimerRequest) -> None:
    if timer.past_due:
        log.info("render_all_hourly running late")
    summary = await service().renderer.render_all()
    log.info("hourly render done: %s", summary)
