"""Capture actual requests and responses. Credentials are redacted before storage."""

import json
from pathlib import Path

import httpx

SENSITIVE = {"authorization", "cookie", "set-cookie", "x-api-key", "x-maplewood-signature"}


def redact(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]"
            if key.lower() in SENSITIVE or key.lower() in {"credentials", "token"}
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class Recorder(httpx.AsyncBaseTransport):
    def __init__(self, inner: httpx.AsyncBaseTransport):
        self.inner, self.records = inner, []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        body = await request.aread()
        response = await self.inner.handle_async_request(request)
        response_body = await response.aread()
        self.records.append(
            {
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": redact(dict(request.headers)),
                    "body": self.decode(body),
                },
                "response": {
                    "status": response.status_code,
                    "headers": redact(dict(response.headers)),
                    "body": self.decode(response_body),
                },
            }
        )
        return response

    @staticmethod
    def decode(data: bytes):
        try:
            return redact(json.loads(data))
        except (ValueError, UnicodeDecodeError):
            return data.decode("utf-8", errors="replace")

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in self.records),
            encoding="utf-8",
        )

    async def aclose(self):
        await self.inner.aclose()
