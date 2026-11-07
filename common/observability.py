"""W3C trace context crosses HTTP calls; prompts and credentials are never attributes."""

import os

from opentelemetry import trace
from opentelemetry.propagators.textmap import Getter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class HeaderGetter(Getter):
    def get(self, carrier, key):
        return [value.decode() for name, value in carrier if name.decode().lower() == key]

    def keys(self, carrier):
        return [name.decode().lower() for name, _ in carrier]


class TraceMiddleware:
    def __init__(self, app, vendor: str, tracer=None):
        self.app, self.vendor = app, vendor
        self.tracer = tracer or trace.get_tracer("maplewood")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] in ("/health", "/.well-known/agent-card.json"):
            await self.app(scope, receive, send)
            return
        parent = TraceContextTextMapPropagator().extract(scope["headers"], getter=HeaderGetter())
        with self.tracer.start_as_current_span(
            f"{self.vendor}.request",
            context=parent,
            kind=trace.SpanKind.SERVER,
            attributes={"maplewood.vendor": self.vendor, "http.request.method": scope["method"]},
        ):
            await self.app(scope, receive, send)


def outgoing_headers() -> dict[str, str]:
    headers = {}
    TraceContextTextMapPropagator().inject(headers)
    return headers


def configure_tracing():
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return None
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    return provider
