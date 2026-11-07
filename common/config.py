"""One source for local addresses, credentials and course paths."""

import json
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
VENDORS = ("venues", "catering", "av", "travel", "print", "concierge")
PORTS = {name: 8100 + index for index, name in enumerate(VENDORS)}
GRPC_PORT = 8204


def grpc_target() -> str:
    return os.environ.get("MAPLEWOOD_GRPC_TARGET", f"127.0.0.1:{GRPC_PORT}")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    host: str = "127.0.0.1"
    llm_provider: str = "ollama"
    llm_model: str = ""
    ollama_host: str = "http://127.0.0.1:11434"
    maplewood_token: str = ""
    database_url: str = ""


def url(vendor: str) -> str:
    overrides = json.loads(os.environ.get("MAPLEWOOD_VENDOR_URLS", "{}"))
    if vendor in overrides:
        return overrides[vendor]
    return f"http://127.0.0.1:{PORTS[vendor]}"


def network_members(module: int) -> tuple[str, ...]:
    if not 0 <= module <= 20:
        raise ValueError("Module must be between 00 and 20.")
    return VENDORS[:1] if module < 5 else VENDORS[: 3 if module < 8 else 6]
