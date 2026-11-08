"""Provider-independent, bounded JSON decisions. Only Tier 2 imports this module."""

import asyncio
import json
import os

import httpx
from jsonschema import ValidationError

from common.config import Settings
from common.http_limits import request_json


class Model:
    def __init__(self, settings: Settings | None = None, transport=None):
        self.settings = settings or Settings()
        self.transport = transport
        if not self.settings.llm_model:
            raise ValueError("Set LLM_MODEL in .env. See .env.example and scripts/check_env.py.")

    async def decide(self, prompt: str) -> dict:
        provider, model = self.settings.llm_provider, self.settings.llm_model
        instruction = "Return one JSON object. Select only the allowed vendors or tool names. Never request credentials.\n"
        headers = {}
        if provider == "ollama":
            endpoint = self.settings.ollama_host + "/api/chat"
            body = {
                "model": model,
                "stream": False,
                "format": "json",
                "messages": [{"role": "user", "content": instruction + prompt}],
            }
        elif provider == "openai":
            endpoint = "https://api.openai.com/v1/responses"
            headers = {"Authorization": "Bearer " + self._key("OPENAI_API_KEY")}
            body = {"model": model, "input": instruction + prompt, "max_output_tokens": 512}
        elif provider == "anthropic":
            endpoint = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self._key("ANTHROPIC_API_KEY"),
                "anthropic-version": "2023-06-01",
            }
            body = {
                "model": model,
                "max_tokens": 512,
                "messages": [{"role": "user", "content": instruction + prompt}],
            }
        elif provider == "gemini":
            endpoint = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            )
            headers = {"x-goog-api-key": self._key("GEMINI_API_KEY")}
            body = {
                "contents": [{"parts": [{"text": instruction + prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "maxOutputTokens": 512,
                },
            }
        else:
            raise ValueError("LLM_PROVIDER must be ollama, openai, anthropic or gemini.")
        try:
            async with httpx.AsyncClient(transport=self.transport, timeout=45) as client:
                data = await request_json(
                    client,
                    "POST",
                    endpoint,
                    json=body,
                    headers=headers,
                    timeout=45,
                    limit=512_000,
                )
        except httpx.HTTPError as exc:
            raise ValueError(
                "Model unavailable. Check .env, your budget, and scripts/check_env.py."
            ) from exc
        if provider == "ollama":
            text = data["message"]["content"]
        elif provider == "anthropic":
            text = "".join(item["text"] for item in data["content"] if item["type"] == "text")
        elif provider == "openai":
            text = "".join(
                part["text"]
                for item in data["output"]
                for part in item.get("content", [])
                if part["type"] == "output_text"
            )
        else:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(text)
        if not isinstance(result, dict):
            raise ValueError("Model response must be a JSON object.")
        return result

    @staticmethod
    def _key(name: str) -> str:
        value = os.environ.get(name, "")
        if not value:
            raise ValueError(
                f"Set {name} in your environment. Graded tasks use scripted models instead."
            )
        return value

    async def tool_decide(self, prompt: str, schema: dict) -> dict:
        from common.model_streams import tool_decision

        try:
            # Both attempts share one deadline. No tool runs during schema repair.
            async with asyncio.timeout(90):
                try:
                    return await tool_decision(self, prompt, schema)
                except ValidationError as exc:
                    if exc.validator not in {"additionalProperties", "required"}:
                        raise
                    correction = (
                        "\nThe previous response did not match the argument structure. "
                        "Call select_action again using exactly these top-level argument keys: "
                        + ", ".join(schema["properties"])
                        + ". Do not add nested tool parameters or event fields."
                    )
                    return await tool_decision(self, prompt + correction, schema)
        except (httpx.HTTPError, TimeoutError, KeyError, TypeError) as exc:
            raise ValueError("Model tool stream unavailable or malformed") from exc


def create_model() -> Model:
    return Model()
