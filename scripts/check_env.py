"""Friendly local diagnostics, without printing secrets."""

import importlib.metadata
import os
import shutil
import socket
import sys

import httpx

from common.config import GRPC_PORT, PORTS, Settings


def model_status(settings, get=httpx.get):
    """Probe only the configured local provider; never make a hosted model call."""
    if settings.llm_provider == "ollama":
        try:
            response = get(settings.ollama_host + "/api/tags", timeout=2)
            response.raise_for_status()
            models = [model["name"] for model in response.json()["models"]]
            available = settings.llm_model in models
            return "Ollama reachable; configured model " + (
                "available."
                if available
                else "not pulled. Run ollama pull with LLM_MODEL from .env."
            )
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return (
                "Ollama unavailable. Start Ollama before using --llm; offline lessons still work."
            )
    variable = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }.get(settings.llm_provider)
    if variable is None:
        return "Unknown LLM_PROVIDER; choose ollama, openai, anthropic or gemini in .env."
    return f"{variable}: " + (
        "set (value hidden)."
        if os.environ.get(variable)
        else "missing; export it in this terminal before using --llm."
    )


def main() -> None:
    print(f"Python {sys.version.split()[0]}; A2A SDK {importlib.metadata.version('a2a-sdk')}")
    for tool in ("uv", "node", "docker", "ollama", "a2a-inspector"):
        print(
            f"{tool}: {'available' if shutil.which(tool) else 'not installed (optional except uv)'}"
        )
    for vendor, port in {**PORTS, "print gRPC": GRPC_PORT}.items():
        with socket.socket() as connection:
            connection.settimeout(0.2)
            listening = connection.connect_ex(("127.0.0.1", port)) == 0
        print(f"{vendor}: port {port} {'in use' if listening else 'free'}")
    settings = Settings()
    print(f"Model provider: {settings.llm_provider}; model configured: {bool(settings.llm_model)}")
    print(model_status(settings))
    print("Tier 1 and all gym tasks need no model, Docker or API keys.")


if __name__ == "__main__":
    main()
