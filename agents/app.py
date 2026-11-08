"""Compose confirmed SDK route factories into a regular FastAPI application."""

import os
from contextlib import asynccontextmanager

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes, create_rest_routes
from a2a.server.routes.common import DefaultServerCallContextBuilder
from a2a.server.tasks import InMemoryTaskStore
from a2a.utils.errors import ExtensionSupportRequiredError
from fastapi import FastAPI
from opentelemetry import trace
from starlette.requests import Request

from agents.catalog import card
from agents.executor import VendorExecutor
from common.binding_policy import ProtocolHeaders
from common.card_trust import published_card
from common.observability import TraceMiddleware
from common.security import BearerGate, Principal


class CallContext(DefaultServerCallContextBuilder):
    def __init__(self, required=()):
        self.required = set(required)

    def build(self, request: Request):
        context = super().build(request)
        context.state["trace_span"] = getattr(request.state, "trace_span", trace.get_current_span())
        if not self.required <= context.requested_extensions:
            raise ExtensionSupportRequiredError()
        principal = getattr(request.state, "principal", None)
        if principal:
            context.state["partner"] = principal.partner
            context.state["authorized_tenant"] = principal.tenant
        return context


def make_handler(vendor: str, *, secure: bool = True, task_store=None, executor=None):
    from a2a.server.cluster.event_stream import TaskEventStream

    return DefaultRequestHandler(
        agent_executor=executor or VendorExecutor(vendor),
        task_store=task_store or InMemoryTaskStore(),
        agent_card=card(vendor, secure=secure),
        extended_agent_card=card(vendor, secure=secure, extended=True)
        if vendor == "travel"
        else None,
        validate_input_modes=True,
        event_stream=task_store if isinstance(task_store, TaskEventStream) else None,
    )


def make_app(
    vendor: str = "venues",
    *,
    tokens: dict[str, Principal] | None = None,
    demo: bool = False,
    handler=None,
    tracer=None,
    verifier=None,
    engine=None,
    agent_card=None,
    rate_budget=None,
    api_key_header=None,
    auth_client=None,
):
    if not demo and not tokens and not verifier:
        raise ValueError("Set MAPLEWOOD_TOKEN or start the network with scripts/network.py.")
    handler = handler or make_handler(vendor, secure=not demo)
    advertised = (
        agent_card or getattr(handler, "course_card", None) or card(vendor, secure=not demo)
    )
    if os.environ.get("MAPLEWOOD_HARDENED") == "1":
        from common.key_rotation import RotatingCardKeys, SharedCardKeys
        from common.security import unb64

        keys = (
            SharedCardKeys(advertised, engine, vendor, unb64(os.environ["MAPLEWOOD_SIGNING_KEY"]))
            if engine
            else RotatingCardKeys(advertised)
        )
        routes = keys.routes()
    else:
        routes = create_agent_card_routes(published_card(advertised, vendor))
    context_builder = CallContext(e.uri for e in advertised.capabilities.extensions if e.required)
    routes += create_jsonrpc_routes(handler, rpc_url="/rpc", context_builder=context_builder)
    routes += create_rest_routes(handler, context_builder=context_builder)

    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            await handler.aclose()
            if engine:
                await engine.dispose()
            if auth_client:
                await auth_client.aclose()

    app = FastAPI(routes=routes, lifespan=lifespan)

    @app.get("/health")
    async def health():
        return {"status": "ready", "vendor": vendor}

    app.state.handler = handler
    traced = TraceMiddleware(ProtocolHeaders(app), vendor, tracer)
    return (
        traced
        if demo
        else BearerGate(
            traced,
            tokens or {},
            verifier=verifier,
            rate_budget=rate_budget,
            api_key_header=api_key_header,
        )
    )
