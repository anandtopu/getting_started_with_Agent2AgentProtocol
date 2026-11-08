"""Final-brief regressions: fail closed, bounded I/O and honest live evidence."""

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from a2a.types import TaskState
from starlette.responses import JSONResponse

from agents import concierge_executor
from common.card_trust import trusted_jwks
from common.config import Settings
from common.http_limits import request_json
from common.identity import RefreshingOIDCVerifier
from common.llm import Model
from common.protocol import request
from common.security import BearerGate, Principal, fetch_file
from scripts import check_live_model


@pytest.mark.parametrize("header,api_key", [(b"authorization", None), (b"x-api-key", "X-API-Key")])
@pytest.mark.parametrize("credentials", [[b"\xff"], [b"\xc3\xa9"], [b"wrong", b"fixture"]])
async def test_malformed_and_duplicate_credentials_are_401(header, api_key, credentials):
    async def forbidden(*args):
        pytest.fail("Unauthenticated request reached the application")

    app = BearerGate(forbidden, {"fixture": Principal("learner")}, api_key_header=api_key)
    values = [(header, value if api_key else b"Bearer " + value) for value in credentials]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://test"
    ) as client:
        response = await client.post("/message:send", headers=values)
        assert response.status_code == 401


async def test_slow_authenticated_body_has_total_deadline():
    async def body():
        yield b"{"
        await asyncio.sleep(1)
        yield b"}"

    app = BearerGate(JSONResponse({}), {"fixture": Principal("learner")}, body_timeout=0.02)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://test"
    ) as client:
        response = await client.post(
            "/message:send", headers={"Authorization": "Bearer fixture"}, content=body()
        )
        assert response.status_code == 408


class SlowStream(httpx.AsyncByteStream):
    def __init__(self):
        self.closed = False

    async def __aiter__(self):
        yield b"{"
        await asyncio.sleep(1)
        yield b"}"

    async def aclose(self):
        self.closed = True


@pytest.mark.parametrize("file", [False, True])
async def test_peer_body_has_total_deadline_and_closes(file):
    stream = SlowStream()
    url = "https://8.8.8.8/file"
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, stream=stream))
    ) as client:
        with pytest.raises((ValueError, httpx.ReadTimeout), match="total time limit"):
            if file:
                await fetch_file(url, {url}, client, timeout=0.02)
            else:
                await request_json(client, "GET", url, timeout=0.02)
    assert stream.closed


async def test_peer_header_wait_has_total_deadline():
    async def slow(_):
        await asyncio.sleep(1)
        return httpx.Response(200, json={})

    async with httpx.AsyncClient(transport=httpx.MockTransport(slow)) as client:
        with pytest.raises(httpx.ReadTimeout, match="total time limit"):
            await request_json(client, "GET", "https://peer.test", timeout=0.02)


class OversizedStream(httpx.AsyncByteStream):
    async def __aiter__(self):
        yield b"x" * 512_001
        pytest.fail("Read beyond the response byte budget")


@pytest.mark.parametrize("consumer", ["json", "file", "model"])
async def test_oversized_response_stops_reading(consumer):
    transport = httpx.MockTransport(lambda _: httpx.Response(200, stream=OversizedStream()))
    with pytest.raises(ValueError, match="size limit"):
        if consumer == "model":
            await Model(Settings(llm_provider="ollama", llm_model="fixture"), transport).decide(
                "Select"
            )
        else:
            async with httpx.AsyncClient(transport=transport) as client:
                if consumer == "file":
                    await fetch_file(
                        "https://8.8.8.8/file", {"https://8.8.8.8/file"}, client, limit=512_000
                    )
                else:
                    await request_json(client, "GET", "https://peer.test", limit=512_000)


@pytest.mark.parametrize(
    "document", [None, [], {}, {"keys": None}, {"keys": [None]}, {"keys": [{}]}]
)
def test_malformed_card_keys_fail_cleanly(document):
    with pytest.raises(ValueError):
        trusted_jwks(document)


@pytest.mark.parametrize("document", [None, [], {"keys": None}, {"keys": [None]}])
async def test_malformed_oidc_keys_fail_closed(document, monkeypatch):
    monkeypatch.setattr(
        "common.identity.jwt.get_unverified_header", lambda _: {"alg": "RS256", "kid": "fixture"}
    )
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=json.dumps(document)))
    ) as client:
        verifier = RefreshingOIDCVerifier(client, "https://issuer.test/keys", "issuer", "audience")
        assert await verifier("fixture") is None


async def test_bounded_requests_never_follow_redirects():
    visited = []

    def redirect(request):
        visited.append(str(request.url))
        return httpx.Response(302, headers={"Location": "https://untrusted.test/"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(redirect), follow_redirects=True
    ) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await request_json(client, "GET", "https://trusted.test/")
    assert visited == ["https://trusted.test/"]


@pytest.mark.parametrize("failure", ["http", "signature", "card", "credentials"])
async def test_discovery_and_setup_failure_finishes_task(monkeypatch, failure):
    emitted = []

    async def enqueue(event):
        emitted.append(event)

    async def discover(*args, **kwargs):
        if failure == "http":
            raise httpx.ConnectError("private peer diagnostic")
        return {"skills": "malformed"} if failure == "card" else {"skills": []}

    async def verify(document, *args):
        if failure == "signature":
            raise ValueError("private signing diagnostic")
        return document

    async def credentials(*args):
        raise ValueError("private credential diagnostic")

    monkeypatch.setattr(concierge_executor, "request_json", discover)
    monkeypatch.setattr(concierge_executor, "verify_discovered", verify)
    monkeypatch.setattr(concierge_executor, "vendor_headers", credentials)
    context = SimpleNamespace(
        current_task=None, message=request({"guests": 40}).message, call_context=None
    )
    await concierge_executor.ConciergeExecutor({"venues": "fixture"}).execute(
        context, SimpleNamespace(enqueue_event=enqueue)
    )
    assert emitted[-1].status.state == TaskState.TASK_STATE_FAILED
    assert "check_env.py" in emitted[-1].status.message.parts[0].text
    assert "private" not in str(emitted[-1])


async def test_live_failure_removes_stale_success_without_printing_peer_content(
    monkeypatch, tmp_path, capsys
):
    output = tmp_path / "workspace/live-model.json"
    output.parent.mkdir()
    output.write_text('{"old": "success"}')
    monkeypatch.setattr(check_live_model, "ROOT", tmp_path)

    def unavailable():
        raise ValueError("PRIVATE-KEY-OR-MODEL-CONTENT")

    monkeypatch.setattr(check_live_model, "create_model", unavailable)
    assert await check_live_model.run_check() == 1
    assert not output.exists()
    diagnostic = capsys.readouterr().err
    assert "check_env.py" in diagnostic
    assert "PRIVATE" not in diagnostic
    assert "Traceback" not in diagnostic
