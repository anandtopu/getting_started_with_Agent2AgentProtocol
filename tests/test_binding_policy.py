"""Direct checks for the transport requirements with contradictory TCK assertions."""

import pytest
from a2a.server.request_handlers.grpc_handler import GrpcHandler
from a2a.types.a2a_pb2 import SendMessageRequest
from a2a.utils.errors import VersionNotSupportedError
from google.protobuf.json_format import ParseDict

from agents.app import make_handler
from common.binding_policy import VersionedGrpcContext
from common.protocol import as_dict, request
from common.testing import ServiceContext, client
from scripts.tck_evidence import (
    REASON,
    unsupported_request,
    validate_grpc_error,
    validate_http_error,
    validate_jsonrpc_error,
)


async def test_http_error_media_and_content_rejection():
    async with client() as http:
        body = as_dict(request({"guests": 40}))
        body["message"]["parts"][0]["mediaType"] = "application/x-unsupported-tck-type"
        response = await http.post("/message:send", json=body)
        validate_http_error(response, code=400, status="INVALID_ARGUMENT", reason=REASON)
        rpc = await http.post(
            "/rpc", json={"jsonrpc": "2.0", "id": 1, "method": "SendMessage", "params": body}
        )
        validate_jsonrpc_error(rpc, 1)
        validate_http_error(
            await http.get("/tasks/course-missing-task"),
            code=404,
            status="NOT_FOUND",
            reason="TASK_NOT_FOUND",
        )
        discovered = await http.get("/.well-known/agent-card.json")
        assert "max-age=" in discovered.headers["cache-control"]


async def test_vendor_grpc_rejects_unsupported_media_with_rich_status():
    class Rejected(Exception):
        pass

    class Context(ServiceContext):
        async def abort(self, code, details, trailing_metadata=()):
            validate_grpc_error(code, details, self.trailing_metadata())
            raise Rejected

    handler = make_handler("venues", secure=False)
    try:
        with pytest.raises(Rejected):
            await GrpcHandler(handler, VersionedGrpcContext()).SendMessage(
                ParseDict(unsupported_request(), SendMessageRequest()),
                Context(),
            )
    finally:
        await handler.aclose()


def test_grpc_rejects_unsupported_and_duplicate_versions():
    class Context:
        def __init__(self, values):
            self.values = values

        def invocation_metadata(self):
            return [("a2a-version", v) for v in self.values]

    for versions in (["99.0"], ["1.0", "99.0"]):
        with pytest.raises(VersionNotSupportedError):
            VersionedGrpcContext().build(Context(versions))
    assert VersionedGrpcContext().build(Context(["1.0"]))
