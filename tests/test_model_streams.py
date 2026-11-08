"""Fragment real provider frames and reject incomplete or unsafe tool responses."""

import json

import httpx
import pytest
from jsonschema import ValidationError

from common.config import Settings
from common.llm import Model

SCHEMA = {
    "type": "object",
    "properties": {"tool": {"enum": ["quote_menu"]}},
    "required": ["tool"],
    "additionalProperties": False,
}


def frames(provider, tool="quote_menu"):
    arguments = json.dumps({"tool": tool})
    if provider == "openai":
        return [
            {
                "type": "response.output_item.added",
                "item": {
                    "type": "function_call",
                    "id": "call1",
                    "name": "select_action",
                    "arguments": "",
                },
            },
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "call1",
                "delta": arguments[:8],
            },
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "call1",
                "delta": arguments[8:],
            },
            {"type": "response.completed", "response": {"status": "completed"}},
        ]
    if provider == "anthropic":
        return [
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {"type": "tool_use", "name": "select_action", "input": {}},
            },
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": arguments[:8]},
            },
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": arguments[8:]},
            },
            {"type": "message_delta", "delta": {"stop_reason": "tool_use"}},
            {"type": "message_stop"},
        ]
    if provider == "ollama":
        return [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "select_action", "arguments": {"tool": tool}}}
                    ]
                }
            },
            {"done": True, "done_reason": "stop"},
        ]
    return [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"functionCall": {"name": "select_action", "args": {"tool": tool}}}
                        ]
                    }
                }
            ]
        },
        {"candidates": [{"finishReason": "STOP"}]},
    ]


class Fragmented(httpx.AsyncByteStream):
    def __init__(self, body):
        self.body = body

    async def __aiter__(self):
        for offset in range(0, len(self.body), 7):
            yield self.body[offset : offset + 7]


@pytest.mark.parametrize("provider", ["ollama", "openai", "anthropic", "gemini"])
@pytest.mark.parametrize("failure", [None, "truncated", "unsafe", "oversized", "partial_frame"])
async def test_tool_streams(provider, failure, monkeypatch):
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.setenv(key, "offline-fixture-key")
    packets = frames(provider, "exfiltrate" if failure == "unsafe" else "quote_menu")
    if failure == "truncated":
        packets.pop()
    text = "".join(
        json.dumps(p) + "\n" if provider == "ollama" else "data: " + json.dumps(p) + "\n\n"
        for p in packets
    )
    if failure == "oversized":
        text = "x" * 64001
    elif failure == "partial_frame":
        text = text[:-1] + "garbage"

    def respond(request):
        body = json.loads(request.content)
        assert body["tools"]
        if provider == "ollama":
            assert body["messages"][0]["role"] == "system"
            assert "Call select_action exactly once" in body["messages"][0]["content"]
        assert "offline-fixture-key" not in request.content.decode()
        return httpx.Response(200, stream=Fragmented(text.encode()))

    model = Model(
        Settings(llm_provider=provider, llm_model="fixture-model"), httpx.MockTransport(respond)
    )
    if failure:
        with pytest.raises((ValueError, ValidationError)):
            await model.tool_decide("Select a safe catering action.", SCHEMA)
    else:
        assert await model.tool_decide("Select a safe catering action.", SCHEMA) == {
            "tool": "quote_menu"
        }
