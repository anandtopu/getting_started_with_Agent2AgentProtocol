"""A configurable vendor bundle: durable tasks, signed card, streaming and verified push."""

import asyncio
from contextlib import asynccontextmanager

import httpx
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import DatabasePushNotificationConfigStore
from a2a.types import AgentCard
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from google.protobuf.json_format import ParseDict
from sqlalchemy.ext.asyncio import create_async_engine

from agents.app import make_app
from agents.catalog import card
from agents.executor import VendorExecutor
from common.cluster import ClusterStore, OutboxSender
from common.delivery import DeliveryStore, durable_receiver
from common.protocol import as_dict, request
from common.security import Principal, sign_card, verify_card
from common.wire import Recorder


@asynccontextmanager
async def vendor_kit(
    database_url: str, tokens: dict, private_key, callback_client, destinations, *, endpoint=None
):
    engine = create_async_engine(database_url)
    callbacks = DatabasePushNotificationConfigStore(engine)
    store = ClusterStore(engine, callbacks=callbacks)
    await store.initialize()
    identity = card("catering")
    if endpoint:
        for interface in identity.supported_interfaces:
            interface.url = endpoint + ("/rpc" if interface.protocol_binding == "JSONRPC" else "")
    identity.capabilities.push_notifications = True
    identity = ParseDict(sign_card(as_dict(identity), private_key, "saffron-kit"), AgentCard())

    async def permitted(url):
        return url in destinations

    handler = DefaultRequestHandler(
        VendorExecutor("catering"),
        store,
        identity,
        push_config_store=callbacks,
        push_sender=OutboxSender(store, callback_client, destinations),
        push_url_validator=permitted,
        event_stream=store,
    )

    async def recover():
        while True:
            await store.dispatch(callback_client, destinations)
            await asyncio.sleep(1)

    worker = asyncio.create_task(recover())
    try:
        yield make_app("catering", tokens=tokens, handler=handler, agent_card=identity), handler
    finally:
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)
        await handler.aclose()
        await engine.dispose()


async def kit_lab(database_url="sqlite+aiosqlite:///:memory:", inbox_path=":memory:"):
    key = Ed25519PrivateKey.generate()
    secret, endpoint = b"synthetic-kit-callback-secret", "http://receiver.test/notifications"
    inbox = DeliveryStore(inbox_path)
    sink = durable_receiver(secret, inbox)
    recorder = Recorder(httpx.ASGITransport(app=sink))
    async with httpx.AsyncClient(transport=recorder) as callback:
        async with vendor_kit(
            database_url, {"fixture": Principal("coordinator")}, key, callback, {endpoint: secret}
        ) as (app, handler):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://kit.test",
                headers={"A2A-Version": "1.0", "Authorization": "Bearer fixture"},
            ) as http:
                identity = (await http.get("/.well-known/agent-card.json")).json()
                verify_card(identity, {"saffron-kit": key.public_key()})
                unauthorized = await http.post(
                    "/message:send",
                    headers={"Authorization": ""},
                    json=as_dict(request({"guests": 40})),
                )
                first_request = as_dict(request({"guests": 40}))
                first_request["configuration"] = {
                    "taskPushNotificationConfig": {"id": "kit", "url": endpoint}
                }
                first = (await http.post("/message:send", json=first_request)).json()["task"]
                followup = request(
                    {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
                )
                second = (await http.post("/message:stream", json=as_dict(followup))).text
                from common.lessons import events

                stream = events(second)
                await handler.aclose()
    result = {
        "signature_verified": True,
        "unauthorized_status": unauthorized.status_code,
        "before": first["status"]["state"],
        "stream": stream,
        "verified_push_deliveries": sink.state.deliveries,
    }
    inbox.close()
    return result
