"""Inkwell: a gRPC-only protocol endpoint plus HTTP card discovery and health."""

import asyncio
import hmac
import os

import grpc
import uvicorn
from a2a.auth.user import User
from a2a.server.request_handlers.grpc_handler import (
    GrpcHandler,
)
from a2a.server.routes import create_agent_card_routes
from a2a.types.a2a_pb2_grpc import add_A2AServiceServicer_to_server
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from agents.app import make_handler
from agents.catalog import card
from common.binding_policy import ProtocolHeaders, VersionedGrpcContext
from common.card_trust import published_card
from common.config import GRPC_PORT, PORTS
from common.observability import inbound_span
from common.tls import grpc_credentials, server_options


class GrpcUser(User):
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def user_name(self) -> str:
        return "maplewood:concierge"


class AuthenticatedContext(VersionedGrpcContext):
    def build_user(self, context):
        # This builder is used only behind TokenInterceptor.
        return GrpcUser()


class TokenInterceptor(grpc.aio.ServerInterceptor):
    """Reject missing tokens and cross-tenant requests before the SDK sees them."""

    def __init__(self, token: str, tracer=None, mtls=False, rate_budget=None):
        self.token = token
        self.tracer = tracer or trace.get_tracer("maplewood")
        self.mtls = mtls
        self.rate_budget = rate_budget

    async def intercept_service(self, continuation, details):
        handler = await continuation(details)
        if handler is None:
            return None
        headers = dict(details.invocation_metadata)
        parent = TraceContextTextMapPropagator().extract(headers)
        authorized = hmac.compare_digest(headers.get("authorization", ""), f"Bearer {self.token}")

        async def check(request, context):
            if self.mtls:
                if b"maplewood-concierge" not in context.auth_context().get("x509_common_name", []):
                    await context.abort(
                        grpc.StatusCode.PERMISSION_DENIED, "Unrecognized client certificate"
                    )
            elif not authorized:
                await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Bearer token required")
            if getattr(request, "tenant", "") not in ("", "maplewood"):
                await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Tenant not authorized")
            if self.rate_budget and not await self.rate_budget.allow("maplewood:concierge"):
                await context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, "Request budget exceeded")

        if handler.unary_unary:

            async def unary(request, context):
                await check(request, context)
                with self.tracer.start_as_current_span(
                    "print.rpc", context=parent, kind=trace.SpanKind.SERVER
                ) as span:
                    token = inbound_span.set(span)
                    try:
                        return await handler.unary_unary(request, context)
                    finally:
                        inbound_span.reset(token)

            return grpc.unary_unary_rpc_method_handler(
                unary,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        if handler.unary_stream:

            async def stream(request, context):
                await check(request, context)
                with self.tracer.start_as_current_span(
                    "print.rpc", context=parent, kind=trace.SpanKind.SERVER
                ) as span:
                    token = inbound_span.set(span)
                    try:
                        async for response in handler.unary_stream(request, context):
                            yield response
                    finally:
                        inbound_span.reset(token)

            return grpc.unary_stream_rpc_method_handler(
                stream,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler


async def serve(token: str, host: str = "127.0.0.1", *, handler=None, engine=None) -> None:
    handler = handler or make_handler("print")
    credentials = grpc_credentials(server=True)
    server = grpc.aio.server(
        interceptors=[
            TokenInterceptor(
                token,
                mtls=bool(credentials),
                rate_budget=handler.task_store if hasattr(handler.task_store, "allow") else None,
            )
        ],
        options=[("grpc.max_receive_message_length", 1_000_000)],
    )
    add_A2AServiceServicer_to_server(GrpcHandler(handler, AuthenticatedContext()), server)
    port = (
        server.add_secure_port(f"{host}:{GRPC_PORT}", credentials)
        if credentials
        else server.add_insecure_port(f"{host}:{GRPC_PORT}")
    )
    if not port:
        raise RuntimeError("Inkwell gRPC port is busy. Run scripts/check_env.py.")
    identity = card("print", grpc_only=True)
    if os.environ.get("MAPLEWOOD_HARDENED") == "1":
        from common.key_rotation import RotatingCardKeys, SharedCardKeys
        from common.security import unb64

        keys = (
            SharedCardKeys(identity, engine, "print", unb64(os.environ["MAPLEWOOD_SIGNING_KEY"]))
            if engine
            else RotatingCardKeys(identity)
        )
        routes = keys.routes()
    else:
        routes = create_agent_card_routes(published_card(identity, "print"))
    app = FastAPI(routes=routes)

    @app.get("/health")
    async def health():
        return {"status": "ready", "vendor": "print", "binding": "GRPC"}

    # Local development only: production transports require TLS at a trusted gateway.
    await server.start()
    try:
        await uvicorn.Server(
            uvicorn.Config(
                ProtocolHeaders(app),
                host=host,
                port=PORTS["print"],
                log_level="info",
                **server_options(),
            )
        ).serve()
    finally:
        await server.stop(grace=2)
        await handler.aclose()
        if engine:
            await engine.dispose()


def run(token: str, host: str = "127.0.0.1", *, handler=None, engine=None) -> None:
    asyncio.run(serve(token, host, handler=handler, engine=engine))
