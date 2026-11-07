"""Exercise provider request/response mappings without keys or network."""

import json

import httpx
import pytest

from common.config import Settings
from common.fakes import ScriptedModel
from common.llm import Model
from common.tool_agent import catering_agent


@pytest.mark.parametrize("provider", ["ollama", "openai", "anthropic", "gemini"])
async def test_provider_mapping(provider, monkeypatch):
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        monkeypatch.setenv(key, "offline-fixture-key")
    text = '{"vendors":["catering"]}'
    replies = {
        "ollama": {"message": {"content": text}},
        "openai": {"output": [{"content": [{"type": "output_text", "text": text}]}]},
        "anthropic": {"content": [{"type": "text", "text": text}]},
        "gemini": {"candidates": [{"content": {"parts": [{"text": text}]}}]},
    }

    def respond(request):
        body = json.loads(request.content)
        assert "offline-fixture-key" not in request.content.decode()
        assert body
        return httpx.Response(200, json=replies[provider])

    model = Model(
        Settings(llm_provider=provider, llm_model="fixture-model"), httpx.MockTransport(respond)
    )
    assert await model.decide("Select a vendor") == {"vendors": ["catering"]}


async def test_unknown_tool_budget():
    with pytest.raises(ValueError, match="three-step"):
        await catering_agent(ScriptedModel([{"tool": "exfiltrate"}] * 3), {"guests": 40})
