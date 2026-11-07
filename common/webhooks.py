"""Authenticated push delivery; HMAC is a Maplewood policy, not an A2A requirement."""

import asyncio
import json
from uuid import uuid4

import httpx
from a2a.server.tasks.push_notification_sender import PushNotificationSender
from a2a.types import StreamResponse
from a2a.utils.proto_utils import to_stream_response
from fastapi import FastAPI, Request
from google.protobuf.json_format import ParseDict
from starlette.responses import JSONResponse

from common.protocol import as_dict
from common.security import verify_webhook, webhook_headers


def receiver(secret: bytes):
    app = FastAPI()
    app.state.deliveries, app.state.seen = [], {}

    @app.post("/notifications")
    async def receive(request: Request):
        body = await request.body()
        if len(body) > 1_000_000:
            return JSONResponse({"error": "Payload too large"}, 413)
        try:
            verify_webhook(body, dict(request.headers), secret, app.state.seen)
            event = ParseDict(json.loads(body), StreamResponse())
            if event.WhichOneof("payload") is None:
                raise ValueError("Empty event")
        except (ValueError, TypeError):
            return JSONResponse({"error": "Notification not verified"}, 401)
        app.state.deliveries.append(as_dict(event))
        return {"accepted": True}

    return app


class SignedPushSender(PushNotificationSender):
    def __init__(self, client: httpx.AsyncClient, config_store, destinations: dict[str, bytes]):
        self.client, self.store, self.destinations = client, config_store, destinations

    async def send_notification(self, task_id, event):
        for config in await self.store.get_info_for_dispatch(task_id):
            if config.url not in self.destinations:
                raise ValueError("Untrusted callback URL")
            body = json.dumps(as_dict(to_stream_response(event)), separators=(",", ":")).encode()
            nonce = str(uuid4())
            headers = webhook_headers(body, self.destinations[config.url], nonce)
            headers["Content-Type"] = "application/a2a+json"
            for attempt in range(3):
                response = await self.client.post(
                    config.url, content=body, headers=headers, follow_redirects=False, timeout=3
                )
                if 200 <= response.status_code < 300:
                    break
                if response.status_code < 500 or attempt == 2:
                    response.raise_for_status()
                await asyncio.sleep(0.01 * 2**attempt)
