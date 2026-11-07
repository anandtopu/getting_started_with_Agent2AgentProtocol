"""Socket-free HTTP clients and a protobuf-roundtrip gRPC service harness.

The gRPC harness calls the real SDK servicer with encoded/decoded messages. It does
not claim to test HTTP/2 framing; network-level gRPC tests are explicitly separate.
"""

import asyncio
from contextlib import asynccontextmanager

import httpx
from a2a.server.request_handlers.grpc_handler import GrpcHandler

from agents.app import make_app, make_handler
from common.config import url
from common.security import Principal
from common.wire import Recorder

TEST_TOKEN = "course-fixture-token-not-for-deployment"


@asynccontextmanager
async def client(
    vendor: str = "venues",
    *,
    demo: bool = False,
    partner: bool = False,
    handler=None,
    records=None,
    tracer=None,
):
    handler = handler or make_handler(vendor, secure=not demo)
    app = make_app(
        vendor,
        demo=demo,
        tokens={TEST_TOKEN: Principal("learner", partner=partner)},
        handler=handler,
        tracer=tracer,
    )
    transport = Recorder(httpx.ASGITransport(app=app))
    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url=url(vendor),
            headers={"Authorization": f"Bearer {TEST_TOKEN}", "A2A-Version": "1.0"},
        ) as http:
            yield http
    finally:
        await asyncio.sleep(0.01)
        if records is not None:
            records.extend(transport.records)
        await handler.aclose()


class ServiceContext:
    def __init__(self):
        self.trailing = ()

    def invocation_metadata(self):
        return (("a2a-version", "1.0"),)

    def trailing_metadata(self):
        return self.trailing

    def set_trailing_metadata(self, value):
        self.trailing = value

    async def abort(self, code, details, trailing_metadata=()):
        raise RuntimeError(f"{code}: {details}")


class InProcessGrpc:
    def __init__(self, vendor: str = "print"):
        self.service = GrpcHandler(make_handler(vendor, secure=False))

    async def unary(self, operation: str, request):
        decoded = type(request).FromString(request.SerializeToString())
        response = await getattr(self.service, operation)(decoded, ServiceContext())
        return type(response).FromString(response.SerializeToString())

    async def stream(self, request):
        decoded = type(request).FromString(request.SerializeToString())
        async for event in self.service.SendStreamingMessage(decoded, ServiceContext()):
            yield type(event).FromString(event.SerializeToString())
