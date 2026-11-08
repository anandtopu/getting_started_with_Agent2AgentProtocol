"""Capture actual requests and responses. Credentials are redacted before storage."""

import json
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

SENSITIVE = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-maplewood-signature",
    "credentials",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "client_secret",
    "password",
    "x-amz-signature",
    "x-amz-security-token",
}


def redact(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in SENSITIVE else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def redact_url(value):
    parsed = urlsplit(value)
    query = parse_qsl(parsed.query, keep_blank_values=True)
    if not any(key.lower() in SENSITIVE for key, _ in query) and parsed.username is None:
        return value
    netloc = parsed.netloc.rsplit("@", 1)[-1]
    return urlunsplit(
        (
            parsed.scheme,
            netloc,
            parsed.path,
            urlencode(
                [(key, "[REDACTED]" if key.lower() in SENSITIVE else item) for key, item in query]
            ),
            parsed.fragment,
        )
    )


def redact_events(text):
    """Reframe multiline SSE data before redaction; never retain unparsed event data."""
    frames, lines, data = [], [], []
    for line in text.splitlines() + [""]:
        if line.startswith("data:"):
            data.append(line[5:].lstrip())
        elif line:
            lines.append(line)
        else:
            if data:
                try:
                    value = json.dumps(redact(json.loads("\n".join(data))))
                except ValueError:
                    value = '"[REDACTED: invalid event JSON]"'
                lines.append("data: " + value)
            if lines:
                frames.append("\n".join(lines))
            lines, data = [], []
    return "\n\n".join(frames) + "\n\n"


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
                    "url": redact_url(str(request.url)),
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
            text = data.decode("utf-8", errors="replace")
            return (
                redact_events(text)
                if any(line.startswith("data:") for line in text.splitlines())
                else text
            )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in self.records),
            encoding="utf-8",
        )

    async def aclose(self):
        await self.inner.aclose()
