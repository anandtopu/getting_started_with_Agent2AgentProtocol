"""Official scenario executor through the course's pinned SDK and transport policies.

This is a loopback-only conformance fixture, never a production vendor or an auth
bypass on the normal server. TCK scenarios prescribe payloads and message IDs.
"""

import asyncio
import importlib.util

import grpc
import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.request_handlers.grpc_handler import GrpcHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes, create_rest_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types.a2a_pb2_grpc import add_A2AServiceServicer_to_server
from starlette.applications import Starlette

from agents.catalog import card
from common.binding_policy import ProtocolHeaders, VersionedGrpcContext
from common.config import ROOT


async def main():
    path = ROOT / "workspace/a2a-tck/sut/a2a-python/sut_agent.py"
    spec = importlib.util.spec_from_file_location("official_tck_scenarios", path)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    identity = card("venues", secure=False)
    identity.name = "Maplewood protocol conformance fixture"
    identity.ClearField("supported_interfaces")
    for binding, endpoint in [
        ("JSONRPC", "http://127.0.0.1:9999"),
        ("HTTP+JSON", "http://127.0.0.1:9999/rest"),
        ("GRPC", "127.0.0.1:10000"),
    ]:
        identity.supported_interfaces.add(
            url=endpoint, protocol_binding=binding, protocol_version="1.0"
        )
    handler = DefaultRequestHandler(
        fixture.TckAgentExecutor(), InMemoryTaskStore(), identity, validate_input_modes=True
    )
    app = ProtocolHeaders(
        Starlette(
            routes=[
                *create_agent_card_routes(identity),
                *create_jsonrpc_routes(handler, rpc_url="/"),
                *create_rest_routes(handler, path_prefix="/rest"),
            ]
        )
    )
    server = grpc.aio.server()
    add_A2AServiceServicer_to_server(GrpcHandler(handler, VersionedGrpcContext()), server)
    if not server.add_insecure_port("127.0.0.1:10000"):
        raise RuntimeError("TCK gRPC port unavailable")
    await server.start()
    try:
        await uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=9999)).serve()
    finally:
        await server.stop(0)
        await handler.aclose()


if __name__ == "__main__":
    asyncio.run(main())
