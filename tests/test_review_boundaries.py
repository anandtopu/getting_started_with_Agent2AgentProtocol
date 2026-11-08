"""Adversarial regressions from the final review against the original brief."""

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from a2a.types import Task
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from agents.concierge import Concierge
from agents.langgraph_vendor import menu_graph
from common.delivery import DeliveryStore, durable_receiver
from common.fakes import ScriptedModel
from common.protocol import request
from common.remote import send
from common.security import b64, verify_card, webhook_headers
from common.testing import client
from common.webhooks import SignedPushSender, receiver
from common.wire import Recorder, redact_url
from scripts import network
from scripts.check_env import model_status


def test_launcher_separates_credentials_and_redacts_status(monkeypatch, tmp_path):
    tokens = {"venues": "venue-secret", "concierge": "caller-secret", "travel": "travel-secret"}
    keys = {name: Ed25519PrivateKey.generate() for name in tokens}
    monkeypatch.setenv("MAPLEWOOD_VENDOR_TOKENS", "inherited-secret")
    for vendor in tokens:
        env = network.child_environment(vendor, tokens, keys, {})
        assert env["MAPLEWOOD_TOKEN"] == tokens[vendor]
        if vendor == "concierge":
            assert json.loads(env["MAPLEWOOD_VENDOR_TOKENS"]) == {
                "venues": "venue-secret",
                "travel": "travel-secret",
            }
        else:
            assert "MAPLEWOOD_VENDOR_TOKENS" not in env
    state = tmp_path / "network.json"
    state.write_text(json.dumps({"module": 8, "tokens": tokens}))
    monkeypatch.setattr(network, "STATE", state)
    status = network.network_status()
    assert "venues" in status and "secret" not in status


async def test_model_cannot_delegate_outside_requested_scope():
    model = ScriptedModel([{"vendors": ["venues", "travel"]}])
    # No client can be invoked: reject the decision before any data leaves.
    with pytest.raises(ValueError, match="requested vendor scope"):
        await Concierge({"venues": None, "travel": None}, model=model).plan(
            {"needs": ["venues"], "guests": 40}
        )


async def test_catering_model_does_not_receive_unrelated_private_fields():
    model = ScriptedModel([{"tool": "quote_menu"}])
    result = await menu_graph(model).ainvoke(
        {
            "brief": {
                "guests": 40,
                "dietary": {"vegan": 40},
                "private_note": "private-secret",
                "user_token": "bearer-secret",
            }
        }
    )
    assert result["result"]["state"] == "TASK_STATE_COMPLETED"
    assert "private-secret" not in model.calls[0] and "bearer-secret" not in model.calls[0]


async def test_each_vendor_receives_only_needed_fields():
    records = []
    async with client("venues", records=records) as venues:
        plan = await Concierge({"venues": venues}).plan(
            {"needs": ["venues"], "guests": 40, "dietary": {"vegan": 40}, "rooms": 20}
        )
    assert plan["delegations"][0]["state"] == "TASK_STATE_COMPLETED"
    assert "dietary" not in json.dumps(records)
    assert '"rooms"' not in json.dumps(records)


@pytest.mark.parametrize(
    "task",
    [
        None,
        {"id": "x", "contextId": "y", "status": {"state": "TASK_STATE_COMPLETED"}},
        {"id": "x", "contextId": "y", "status": {"state": "TASK_STATE_WORKING"}},
        {"id": "x", "contextId": "y", "status": {"state": "invented"}},
        {
            "id": "x",
            "contextId": "y",
            "status": {"state": "TASK_STATE_COMPLETED"},
            "artifacts": [None],
        },
    ],
)
async def test_bad_vendor_response_does_not_abort_other_delegations(task):
    async with (
        client("venues") as venues,
        httpx.AsyncClient(
            transport=httpx.MockTransport(lambda req: httpx.Response(200, json={"task": task})),
            base_url="https://catering.test",
        ) as catering,
    ):
        plan = await Concierge({"venues": venues, "catering": catering}).plan({"guests": 40})
    assert [item["state"] for item in plan["delegations"]] == [
        "TASK_STATE_COMPLETED",
        "TASK_STATE_FAILED",
    ]
    assert plan["total_cents"] == plan["delegations"][0]["quotes"][0]["total_cents"]


@pytest.mark.parametrize(
    "signed",
    [
        None,
        {"signatures": None},
        {"signatures": [None]},
        {"signatures": [{"protected": b64(b"[]"), "signature": "invalid"}]},
    ],
)
def test_malformed_signature_is_a_validation_failure(signed):
    with pytest.raises(ValueError):
        verify_card(signed, {})


@pytest.mark.parametrize("durable", [False, True])
async def test_signed_malformed_webhook_is_rejected(durable):
    secret, body = b"fixture-secret", b'{"task":{"unknownField":"bad"}}'
    store = DeliveryStore(":memory:")
    app = durable_receiver(secret, store) if durable else receiver(secret)
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://callback.test"
        ) as http:
            response = await http.post(
                "/notifications", content=body, headers=webhook_headers(body, secret, "one")
            )
        assert response.status_code == 401
        assert not app.state.deliveries
    finally:
        store.close()


async def test_webhook_stops_reading_at_size_limit():
    async def chunks():
        yield b"x" * 1_000_001
        raise AssertionError("Receiver read beyond its limit")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=receiver(b"fixture")), base_url="http://callback.test"
    ) as http:
        assert (await http.post("/notifications", content=chunks())).status_code == 413


async def test_push_retries_transient_connection_failure():
    calls = []

    async def transport(request):
        calls.append(request)
        if len(calls) == 1:
            raise httpx.ConnectError("Temporary outage")
        return httpx.Response(200, json={"accepted": True})

    class Configs:
        async def get_info_for_dispatch(self, task_id):
            return [SimpleNamespace(url="http://callback.test/notifications")]

    async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as http:
        await SignedPushSender(
            http, Configs(), {"http://callback.test/notifications": b"fixture"}
        ).send_notification("task", Task(id="task", context_id="context"))
    assert len(calls) == 2
    assert calls[0].content == calls[1].content
    assert calls[0].headers["x-maplewood-nonce"] == calls[1].headers["x-maplewood-nonce"]


def test_wire_redacts_multiline_events_and_signed_query_secrets():
    event = b'data: {"task": {"metadata":\ndata: {"token":"private-secret", "client_secret":"oauth-secret"}}}\n\n'
    captured = Recorder.decode(event)
    assert "private-secret" not in captured and "oauth-secret" not in captured
    assert json.loads(captured.removeprefix("data: "))["task"]["metadata"]["token"] == "[REDACTED]"
    url = redact_url("https://user:password@files.test/file?token=query-secret&name=plan")
    assert all(secret not in url for secret in ("password", "query-secret", "user:"))
    assert "name=plan" in url


def test_model_diagnostics_reveal_presence_without_secrets(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-secret")
    result = model_status(SimpleNamespace(llm_provider="openai"))
    assert "set" in result and "fixture-secret" not in result
    monkeypatch.delenv("OPENAI_API_KEY")
    assert "missing" in model_status(SimpleNamespace(llm_provider="openai"))
    settings = SimpleNamespace(
        llm_provider="ollama", ollama_host="http://local", llm_model="fixture"
    )
    result = model_status(
        settings,
        get=lambda *args, **kwargs: httpx.Response(
            200,
            json={"models": [{"name": "fixture"}]},
            request=httpx.Request("GET", "http://local/api/tags"),
        ),
    )
    assert "available" in result


async def test_vendor_response_has_streaming_size_limit():
    class TooLarge(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"x" * 1_000_001
            raise AssertionError("Read beyond the response size limit")

    async with httpx.AsyncClient(
        base_url="https://vendor.test",
        transport=httpx.MockTransport(lambda req: httpx.Response(200, stream=TooLarge())),
    ) as http:
        with pytest.raises(ValueError, match="byte budget"):
            await send(http, request({"guests": 40}))


async def test_slow_vendor_has_overall_deadline(monkeypatch):
    monkeypatch.setenv("MAPLEWOOD_VENDOR_TIMEOUT", "0.01")

    class Slow(httpx.AsyncByteStream):
        async def __aiter__(self):
            await asyncio.sleep(1)
            yield b"{}"

    async with httpx.AsyncClient(
        base_url="https://vendor.test",
        transport=httpx.MockTransport(lambda req: httpx.Response(200, stream=Slow())),
    ) as http:
        with pytest.raises(httpx.ReadTimeout, match="overall deadline"):
            await send(http, request({"guests": 40}))
