"""Friendly local diagnostics, without printing secrets."""

import importlib.metadata
import shutil
import socket
import sys

from common.config import PORTS, Settings


def main() -> None:
    print(f"Python {sys.version.split()[0]}; A2A SDK {importlib.metadata.version('a2a-sdk')}")
    for tool in ("uv", "node", "docker", "ollama", "a2a-inspector"):
        print(
            f"{tool}: {'available' if shutil.which(tool) else 'not installed (optional except uv)'}"
        )
    for vendor, port in PORTS.items():
        with socket.socket() as connection:
            connection.settimeout(0.2)
            listening = connection.connect_ex(("127.0.0.1", port)) == 0
        print(f"{vendor}: port {port} {'in use' if listening else 'free'}")
    settings = Settings()
    print(f"Model provider: {settings.llm_provider}; model configured: {bool(settings.llm_model)}")
    print("Tier 1 and all gym tasks need no model, Docker or API keys.")


if __name__ == "__main__":
    main()
