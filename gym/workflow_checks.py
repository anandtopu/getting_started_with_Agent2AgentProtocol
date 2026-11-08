"""Trusted offline workflow fixtures; applications use real SDK transports."""

import json
from contextlib import AsyncExitStack

import httpx

from agents.app import make_handler
from agents.concierge import Concierge
from agents.langgraph_vendor import LangGraphCatering
from agents.mcp_executor import KitchenExecutor
from common.config import Settings
from common.fakes import ScriptedModel
from common.lessons import events
from common.llm import Model
from common.manual_server import manual_app
from common.protocol import as_dict, request
from common.security import webhook_headers
from common.testing import client


def native_frames(provider, tool):
    arguments = {"tool": tool}
    if provider == "openai":
        return [
            {
                "type": "response.output_item.added",
                "item": {
                    "type": "function_call",
                    "id": "one",
                    "name": "select_action",
                    "arguments": "",
                },
            },
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "one",
                "delta": json.dumps(arguments),
            },
            {"type": "response.completed", "response": {"status": "completed"}},
        ]
    if provider == "anthropic":
        return [
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {"type": "tool_use", "name": "select_action"},
            },
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": json.dumps(arguments)},
            },
            {"type": "message_delta", "delta": {"stop_reason": "tool_use"}},
            {"type": "message_stop"},
        ]
    if provider == "gemini":
        return [
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"functionCall": {"name": "select_action", "args": arguments}}
                            ]
                        }
                    }
                ]
            },
            {"candidates": [{"finishReason": "STOP"}]},
        ]
    return [
        {
            "message": {
                "tool_calls": [{"function": {"name": "select_action", "arguments": arguments}}]
            }
        },
        {"done": True},
    ]


async def check(kind, learner):
    family, action = kind.split(":")
    async with AsyncExitStack() as stack:
        if family == "manual":
            http = await stack.enter_async_context(
                httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=manual_app()), base_url="http://manual.test"
                )
            )
            envelope = {
                "jsonrpc": "2.0",
                "id": "exchange-9",
                "method": "SendMessage",
                "params": as_dict(request({"guests": 40})),
            }
            initial = (await http.post("/rpc", json=envelope)).json()["result"]["task"]
            if action in {"get", "missing"}:
                envelope.update(
                    method="GetTask", params={"id": initial["id"] if action == "get" else "absent"}
                )
            elif action == "method":
                envelope["method"] = "InventedOperation"
            elif action == "rejected":
                envelope["params"] = as_dict(request({"guests": 1000}))
            result = await learner.exercise(
                {
                    "http": http,
                    "arguments": {"content": "{"} if action == "parse" else {"json": envelope},
                }
            )
            assert isinstance(result, dict), "Return the RPC response."
            if action in {"missing", "parse", "method"}:
                assert (
                    result["error"]["code"]
                    == {"missing": -32001, "parse": -32700, "method": -32601}[action]
                )
            elif action == "get":
                assert result["result"] == initial
            else:
                assert result["id"] == envelope["id"]
                assert result["result"]["task"]["status"]["state"] == (
                    "TASK_STATE_REJECTED" if action == "rejected" else "TASK_STATE_COMPLETED"
                )
        elif family == "native_model":
            provider = action if action not in {"unsafe", "truncated"} else "ollama"
            packets = native_frames(provider, "exfiltrate" if action == "unsafe" else "quote_menu")
            if action == "truncated":
                packets.pop()
            body = "".join(
                json.dumps(p) + "\n" if provider == "ollama" else "data: " + json.dumps(p) + "\n\n"
                for p in packets
            )
            model = Model(
                Settings(llm_provider=provider, llm_model="offline"),
                httpx.MockTransport(lambda req: httpx.Response(200, text=body)),
            )
            model._key = lambda name: "synthetic-offline-key"
            schema = {
                "type": "object",
                "properties": {"tool": {"enum": ["quote_menu"]}},
                "required": ["tool"],
                "additionalProperties": False,
            }
            result = await learner.exercise({"model": model, "schema": schema})
            assert result == (
                {"rejected": True} if action in {"unsafe", "truncated"} else {"tool": "quote_menu"}
            )
        elif family == "orchestration":
            clients = {
                vendor: await stack.enter_async_context(client(vendor))
                for vendor in ("venues", "catering")
            }
            brief = {"guests": 40, "dietary": {"vegan": 40}}
            context = {"clients": clients, "brief": brief}
            if action == "resume":
                context["previous"] = await Concierge(clients).plan({"guests": 40})
            elif action in {"untrusted", "private"}:
                context["model"] = ScriptedModel(
                    [{"vendors": ["rogue" if action == "untrusted" else "venues"]}]
                )
                brief["private_note"] = "sensitive-diary"
            elif action == "rejected":
                brief["guests"] = 1000
            elif action == "fallback":

                def fail(req):
                    raise httpx.ConnectError("synthetic outage")

                context["fallbacks"] = {"venues": clients["venues"]}
                clients["venues"] = await stack.enter_async_context(
                    httpx.AsyncClient(
                        transport=httpx.MockTransport(fail), base_url="http://unavailable.test"
                    )
                )
            result = await learner.exercise(context)
            assert isinstance(result, dict), "Return the completed plan or rejection."
            if action == "untrusted":
                assert result == {"rejected_selection": True}
            else:
                assert result["approval_required"]
                assert all(
                    d["state"]
                    == ("TASK_STATE_REJECTED" if action == "rejected" else "TASK_STATE_COMPLETED")
                    for d in result["delegations"]
                )
                if action == "resume":
                    assert [d["task_id"] for d in result["delegations"]] == [
                        d["task_id"] for d in context["previous"]["delegations"]
                    ]
                if action == "private":
                    assert "sensitive-diary" not in context["model"].calls[0]
        elif family in {"framework", "mcp"}:
            if family == "mcp" and action in {"capacity", "too_many", "invalid"}:
                result = await learner.exercise(
                    {"guests": {"capacity": 60, "too_many": 301, "invalid": 0}[action]}
                )
                assert isinstance(result, dict), "Return the MCP result or a rejection."
                assert (
                    result.get("available") is True
                    if action == "capacity"
                    else result == {"rejected": True}
                )
                return
            model = ScriptedModel(
                [{"tool": "exfiltrate" if action == "unsafe" else "quote_menu"} for _ in range(2)]
            )
            executor = LangGraphCatering(model) if family == "framework" else KitchenExecutor()
            http = await stack.enter_async_context(
                client("catering", handler=make_handler("catering", executor=executor))
            )
            brief = {"guests": 40, "dietary": {"vegan": 40}}
            context = {
                "http": http,
                "brief": brief,
                "path": "/message:stream" if action == "stream" else "/message:send",
            }
            if action == "pause":
                brief.pop("dietary")
            elif action in {"capacity", "reject"}:
                brief["guests"] = 400
            elif action == "resume":
                first = (
                    await http.post("/message:send", json=as_dict(request({"guests": 40})))
                ).json()["task"]
                context.update(task_id=first["id"], context_id=first["contextId"])
            result = await learner.exercise(context)
            if action == "stream":
                assert isinstance(result, str), "Return the captured SSE stream."
                assert (
                    events(result)[-1]["statusUpdate"]["status"]["state"] == "TASK_STATE_COMPLETED"
                )
            else:
                assert isinstance(result, dict), "Return the A2A response."
                expected = {
                    "pause": "INPUT_REQUIRED",
                    "unsafe": "FAILED",
                    "capacity": "FAILED",
                    "reject": "REJECTED",
                }.get(action, "COMPLETED")
                assert result["task"]["status"]["state"] == "TASK_STATE_" + expected
                if action == "resume":
                    assert result["task"]["id"] == context["task_id"]
        elif family == "egress":
            if action == "replay":
                body, secret = b'{"task":{"id":"one"}}', b"synthetic-secret"
                assert (
                    await learner.exercise(
                        {
                            "body": body,
                            "secret": secret,
                            "headers": webhook_headers(body, secret, "one", 100),
                        }
                    )
                    is True
                )
                return
            url = "https://127.0.0.1/file" if action == "private_ip" else "https://8.8.8.8/file"
            http = await stack.enter_async_context(
                httpx.AsyncClient(
                    transport=httpx.MockTransport(
                        lambda req: httpx.Response(
                            302 if action == "redirect" else 200,
                            content=b"x" * (65 if action == "oversize" else 10),
                            headers={"location": "https://127.0.0.1/"},
                        )
                    )
                )
            )
            result = await learner.exercise(
                {"url": url, "allowed": set() if action == "unlisted" else {url}, "http": http}
            )
            # A starter returning None must fail, even when rejecting malicious input.
            if action != "valid":
                assert result is None
                valid = await learner.exercise(
                    {
                        "url": "https://8.8.8.8/file",
                        "allowed": {"https://8.8.8.8/file"},
                        "http": await stack.enter_async_context(
                            httpx.AsyncClient(
                                transport=httpx.MockTransport(
                                    lambda req: httpx.Response(200, content=b"ok")
                                )
                            )
                        ),
                    }
                )
                assert valid == b"ok", "Also accept an explicitly approved bounded response."
            else:
                assert result == b"x" * 10
        else:
            raise ValueError("Unknown workflow family")
