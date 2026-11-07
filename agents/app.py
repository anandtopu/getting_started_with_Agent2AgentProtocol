"""Compose confirmed SDK route factories into a regular FastAPI application."""

from contextlib import asynccontextmanager

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes, create_rest_routes
from a2a.server.routes.common import DefaultServerCallContextBuilder
from a2a.server.tasks import InMemoryTaskStore
from fastapi import FastAPI
from starlette.requests import Request

from agents.catalog import card
from agents.executor import VendorExecutor
from common.card_trust import published_card
from common.observability import TraceMiddleware
from common.security import BearerGate, Principal


class CallContext(DefaultServerCallContextBuilder):
    def build(self, request: Request):
        context = super().build(request)
        principal = getattr(request.state, "principal", None)
        if principal:
            context.state["partner"] = principal.partner
            context.state["authorized_tenant"] = principal.tenant
        return context


def make_handler(vendor: str, *, secure: bool = True, task_store=None, executor=None):
    return DefaultRequestHandler(
        agent_executor=executor or VendorExecutor(vendor),
        task_store=task_store or InMemoryTaskStore(),
        agent_card=card(vendor, secure=secure),
        extended_agent_card=card(vendor, secure=secure, extended=True)
        if vendor == "travel"
        else None,
        validate_input_modes=True,
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
):
    if not demo and not tokens and not verifier:
        raise ValueError("Set MAPLEWOOD_TOKEN or start the network with scripts/network.py.")
    handler = handler or make_handler(vendor, secure=not demo)
    routes = create_agent_card_routes(published_card(card(vendor, secure=not demo), vendor))
    routes += create_jsonrpc_routes(handler, rpc_url="/rpc", context_builder=CallContext())
    routes += create_rest_routes(handler, context_builder=CallContext())

    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            await handler.aclose()
            if engine:
                await engine.dispose()

    app = FastAPI(routes=routes, lifespan=lifespan)

    @app.get("/health")
    async def health():
        return {"status": "ready", "vendor": vendor}

    app.state.handler = handler
    traced = TraceMiddleware(app, vendor, tracer)
    return traced if demo else BearerGate(traced, tokens or {}, verifier=verifier)
