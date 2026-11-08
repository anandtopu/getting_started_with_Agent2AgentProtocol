"""Transport policies not supplied by the SDK's route factories."""

from a2a.server.request_handlers.grpc_handler import DefaultGrpcServerCallContextBuilder
from a2a.utils.errors import VersionNotSupportedError
from opentelemetry import trace

from common.observability import inbound_span


class VersionedGrpcContext(DefaultGrpcServerCallContextBuilder):
    def build(self, context):
        versions = [
            value for key, value in context.invocation_metadata() if key.lower() == "a2a-version"
        ]
        if versions and (len(versions) != 1 or versions[0] != "1.0"):
            raise VersionNotSupportedError()
        result = super().build(context)
        result.state["trace_span"] = inbound_span.get() or trace.get_current_span()
        return result


class ProtocolHeaders:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def headers(message):
            if message["type"] == "http.response.start":
                values = list(message.get("headers", []))
                path = scope.get("path", "")
                if path in {"/.well-known/agent-card.json", "/.well-known/jwks.json"}:
                    values = [(k, v) for k, v in values if k.lower() != b"cache-control"]
                    values.append((b"cache-control", b"public, max-age=30"))
                elif message["status"] >= 400 and path != "/rpc" and path != "/":
                    values = [(k, v) for k, v in values if k.lower() != b"content-type"]
                    values.append((b"content-type", b"application/a2a+json"))
                message = {**message, "headers": values}
            await send(message)

        await self.app(scope, receive, headers)
