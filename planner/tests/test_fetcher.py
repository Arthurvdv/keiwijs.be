from __future__ import annotations

import httpx
import pytest
import respx

from ssfilter import fetcher

GOOD = (
    "https://school.smartschool.be/planner/sync/ics/"
    "e2ed7bf1-269c-499b-ba8a-5ddc3596d59c/e0c9355d-6573-518e-82e0-888b9d33e772"
)
ICS = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nEND:VCALENDAR\r\n"


@pytest.fixture(autouse=True)
def _no_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    async def ok(_host: str) -> None:
        return None

    monkeypatch.setattr(fetcher, "assert_public_host", ok)


@pytest.mark.parametrize(
    "url",
    [
        GOOD,
        GOOD + "/",
        GOOD + "?x=1#frag",
        GOOD.replace("https://school", "HTTPS://School"),
        " " + GOOD + " ",
    ],
)
def test_normalise_accepts_and_canonicalises(url: str) -> None:
    assert fetcher.normalise_url(url) == GOOD


@pytest.mark.parametrize(
    ("url", "kind"),
    [
        ("http://school.smartschool.be/planner/sync/ics/a/b", "invalid_url"),
        ("https://evil.com/planner/sync/ics/a/b", "blocked"),
        ("https://school.smartschool.be.evil.com/planner/sync/ics/a/b", "blocked"),
        ("https://school.smartschool.be@evil.com/planner/sync/ics/a/b", "invalid_url"),
        ("https://school.smartschool.be:8443/planner/sync/ics/a/b", "invalid_url"),
        ("https://smartschool.be/planner/sync/ics/a/b", "blocked"),
        ("https://1.2.3.4/planner/sync/ics/a/b", "blocked"),
        ("https://school.smartschool.be/login", "blocked"),
        ("https://school.smartschool.be/planner/sync/ics/not-a-uuid/x", "blocked"),
        ("", "invalid_url"),
        ("https://school.smartschool.be/" + "a" * 2000, "invalid_url"),
        ("not a url", "invalid_url"),
    ],
)
def test_normalise_rejects(url: str, kind: str) -> None:
    with pytest.raises(fetcher.UpstreamError) as exc:
        fetcher.normalise_url(url)
    assert exc.value.kind == kind


@pytest.mark.parametrize(
    ("ip", "public"),
    [
        ("8.8.8.8", True),
        ("10.0.0.1", False),
        ("127.0.0.1", False),
        ("169.254.169.254", False),
        ("192.168.1.1", False),
        ("::1", False),
        ("::ffff:10.0.0.1", False),
        ("2a00:1450:4001::1", True),
        ("0.0.0.0", False),
        ("garbage", False),
    ],
)
def test_is_public_ip(ip: str, public: bool) -> None:
    assert fetcher.is_public_ip(ip) is public


@respx.mock
async def test_fetch_ok() -> None:
    respx.get(GOOD).mock(return_value=httpx.Response(200, content=ICS))
    async with httpx.AsyncClient() as client:
        up = await fetcher.fetch_ics(GOOD, client)
    assert up.body == ICS and up.final_url == GOOD


@respx.mock
async def test_fetch_follows_allowed_redirect_only() -> None:
    other = GOOD.replace("e0c9355d", "aaaaaaaa")
    respx.get(GOOD).mock(return_value=httpx.Response(301, headers={"location": other}))
    respx.get(other).mock(return_value=httpx.Response(200, content=ICS))
    async with httpx.AsyncClient() as client:
        up = await fetcher.fetch_ics(GOOD, client)
    assert up.final_url == other


@respx.mock
async def test_fetch_blocks_redirect_off_allowlist() -> None:
    respx.get(GOOD).mock(
        return_value=httpx.Response(302, headers={"location": "http://169.254.169.254/latest"})
    )
    async with httpx.AsyncClient() as client:
        with pytest.raises(fetcher.UpstreamError) as exc:
            await fetcher.fetch_ics(GOOD, client)
    assert exc.value.kind == "invalid_url"


@respx.mock
async def test_fetch_redirect_loop() -> None:
    respx.get(GOOD).mock(return_value=httpx.Response(302, headers={"location": GOOD}))
    async with httpx.AsyncClient() as client:
        with pytest.raises(fetcher.UpstreamError) as exc:
            await fetcher.fetch_ics(GOOD, client)
    assert exc.value.kind == "redirect"


@respx.mock
@pytest.mark.parametrize(
    ("response", "kind"),
    [
        (httpx.Response(500), "http_status"),
        (httpx.Response(404), "http_status"),
        (httpx.Response(200, content=b"<html>login</html>"), "not_ics"),
        (httpx.Response(200, content=b"x" * (fetcher.MAX_BODY_BYTES + 1)), "too_large"),
    ],
)
async def test_fetch_error_kinds(response: httpx.Response, kind: str) -> None:
    respx.get(GOOD).mock(return_value=response)
    async with httpx.AsyncClient() as client:
        with pytest.raises(fetcher.UpstreamError) as exc:
            await fetcher.fetch_ics(GOOD, client)
    assert exc.value.kind == kind


@respx.mock
async def test_fetch_timeout() -> None:
    respx.get(GOOD).mock(side_effect=httpx.ReadTimeout("slow"))
    async with httpx.AsyncClient() as client:
        with pytest.raises(fetcher.UpstreamError) as exc:
            await fetcher.fetch_ics(GOOD, client)
    assert exc.value.kind == "timeout"


@respx.mock
async def test_fetch_tolerates_bom_and_sends_ua() -> None:
    route = respx.get(GOOD).mock(return_value=httpx.Response(200, content=b"\xef\xbb\xbf" + ICS))
    async with httpx.AsyncClient() as client:
        await fetcher.fetch_ics(GOOD, client, user_agent="TestAgent/1")
    assert route.calls.last.request.headers["user-agent"] == "TestAgent/1"


async def test_private_dns_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    async def fake_getaddrinfo(*_a: object, **_k: object) -> list[tuple[object, ...]]:
        return [(None, None, None, None, ("10.1.2.3", 443))]

    monkeypatch.undo()  # drop the autouse no-op so the real check runs
    loop = asyncio.get_running_loop()
    monkeypatch.setattr(loop, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(fetcher.UpstreamError) as exc:
        await fetcher.assert_public_host("school.smartschool.be")
    assert exc.value.kind == "blocked"
