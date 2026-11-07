"""A propagated header, rather than a local nested block, establishes parentage."""

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agents.concierge import Concierge
from common.testing import client


async def test_trace_crosses_http_boundary():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("maplewood.test")
    records = []
    async with client("venues", tracer=tracer, records=records) as vendor:
        with tracer.start_as_current_span("concierge.plan") as root:
            await Concierge({"venues": vendor}).plan({"needs": ["venues"], "guests": 40})
            root_id = root.get_span_context().span_id
    spans = exporter.get_finished_spans()
    remote = next(s for s in spans if s.name == "venues.request")
    assert remote.parent.span_id == root_id
    assert len({s.context.trace_id for s in spans}) == 1
    assert "traceparent" in records[0]["request"]["headers"]
    provider.shutdown()


async def test_trace_crosses_grpc_metadata_boundary():
    from types import SimpleNamespace

    import grpc

    from agents.grpc_server import TokenInterceptor
    from common.observability import outgoing_headers
    from common.protocol import request

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("maplewood.grpc.test")

    async def operation(message, context):
        return message

    async def continuation(details):
        return grpc.unary_unary_rpc_method_handler(operation)

    with tracer.start_as_current_span("concierge.plan") as root:
        metadata = {"authorization": "Bearer test", **outgoing_headers()}
        root_id = root.get_span_context().span_id
    interceptor = TokenInterceptor("test", tracer)
    wrapped = await interceptor.intercept_service(
        continuation, SimpleNamespace(invocation_metadata=tuple(metadata.items()))
    )
    await wrapped.unary_unary(request({"guests": 40}), None)
    remote = next(s for s in exporter.get_finished_spans() if s.name == "print.rpc")
    assert remote.parent.span_id == root_id
    assert remote.context.trace_id == root.get_span_context().trace_id
    provider.shutdown()
