"""Direct checks for the transport requirements with contradictory TCK assertions."""

import pytest
from a2a.utils.errors import VersionNotSupportedError

from common.binding_policy import VersionedGrpcContext
from common.protocol import as_dict, request
from common.testing import client


async def test_http_error_media_and_content_rejection():
    async with client() as http:
        body = as_dict(request({"guests": 40}))
        body["message"]["parts"][0]["mediaType"] = "application/x-unsupported-tck-type"
        response = await http.post("/message:send", json=body)
        assert response.status_code == 400
        assert response.headers["content-type"] == "application/a2a+json"
        assert response.json()["error"]["status"] == "INVALID_ARGUMENT"
        rpc = await http.post(
            "/rpc", json={"jsonrpc": "2.0", "id": 1, "method": "SendMessage", "params": body}
        )
        assert rpc.json()["error"]["code"] == -32005
        discovered = await http.get("/.well-known/agent-card.json")
        assert "max-age=" in discovered.headers["cache-control"]


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
