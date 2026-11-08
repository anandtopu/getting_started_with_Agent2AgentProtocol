"""Independent wire checks for obligations obscured by four pinned TCK defects.

These checks supplement the raw official report; they never patch its tests,
change its results, or accept an error on the strength of its message alone.
"""

import base64
import uuid

import grpc
import httpx
from a2a.types.a2a_pb2 import SendMessageRequest
from a2a.types.a2a_pb2_grpc import A2AServiceStub
from google.protobuf.json_format import ParseDict
from google.rpc import error_details_pb2, status_pb2

ERROR_INFO = "type.googleapis.com/google.rpc.ErrorInfo"
MEDIA = "application/x-unsupported-tck-type"
REASON = "CONTENT_TYPE_NOT_SUPPORTED"


def unsupported_request():
    return {
        "message": {
            "role": "ROLE_USER",
            "messageId": "course-conformance-" + uuid.uuid4().hex,
            "parts": [{"raw": "dGNr", "mediaType": MEDIA}],
        }
    }


def validate_details(details, reason):
    assert isinstance(details, list) and details, "Missing typed error details"
    for detail in details:
        assert isinstance(detail, dict) and isinstance(detail.get("@type"), str), (
            "Each error detail needs a type URL"
        )
        assert detail["@type"], "Empty error detail type URL"
    identities = [d for d in details if d["@type"] == ERROR_INFO]
    assert len(identities) == 1, "Expected exactly one ErrorInfo identity"
    identity = identities[0]
    assert identity.get("reason") == reason, "Incorrect A2A error reason"
    assert identity.get("domain") == "a2a-protocol.org", "Incorrect A2A error domain"
    ParseDict({k: v for k, v in identity.items() if k != "@type"}, error_details_pb2.ErrorInfo())


def validate_http_error(response, *, code, status, reason):
    assert response.status_code == code, "Incorrect HTTP status"
    assert response.headers["content-type"].split(";", 1)[0].strip() == "application/a2a+json"
    body = response.json()
    assert isinstance(body, dict) and set(body) == {"error"}, "Incorrect REST error envelope"
    error = body["error"]
    assert isinstance(error, dict), "Missing REST error object"
    assert type(error.get("code")) is int and error["code"] == code
    assert error.get("status") == status
    assert isinstance(error.get("message"), str) and error["message"]
    validate_details(error.get("details"), reason)
    return {
        "http_status": response.status_code,
        "content_type": response.headers["content-type"],
        "body": body,
    }


def validate_jsonrpc_error(response, request_id):
    assert response.status_code == 200
    body = response.json()
    assert body.get("jsonrpc") == "2.0" and body.get("id") == request_id
    assert "result" not in body, "A rejection must not also contain a result"
    error = body["error"]
    assert type(error.get("code")) is int and error["code"] == -32005
    assert isinstance(error.get("message"), str) and error["message"]
    if "data" in error:
        validate_details(error["data"], REASON)
    return body


def validate_grpc_error(code, message, trailing_metadata):
    assert code == grpc.StatusCode.INVALID_ARGUMENT, "Incorrect gRPC status"
    assert isinstance(message, str) and message
    encoded = [v for k, v in trailing_metadata if k == "grpc-status-details-bin"]
    assert len(encoded) == 1, "Missing or duplicated rich gRPC status"
    status = status_pb2.Status.FromString(encoded[0])
    assert status.code == code.value[0] and status.message == message
    identities = []
    for detail in status.details:
        assert detail.type_url, "Missing protobuf Any type URL"
        if detail.Is(error_details_pb2.ErrorInfo.DESCRIPTOR):
            info = error_details_pb2.ErrorInfo()
            assert detail.Unpack(info)
            identities.append(info)
    assert len(identities) == 1, "Expected exactly one gRPC ErrorInfo identity"
    assert identities[0].reason == REASON and identities[0].domain == "a2a-protocol.org"
    return {
        "code": status.code,
        "message": status.message,
        "reason": identities[0].reason,
        "domain": identities[0].domain,
        "status_details_bin_base64": base64.b64encode(encoded[0]).decode("ascii"),
    }


def verify_wire_obligations():
    """Exercise the same running fixture as the TCK with independent assertions."""
    evidence = {}
    with httpx.Client(
        base_url="http://127.0.0.1:9999", timeout=5, trust_env=False, headers={"A2A-Version": "1.0"}
    ) as http:
        evidence["http_missing_task"] = validate_http_error(
            http.get("/rest/tasks/course-missing-" + uuid.uuid4().hex),
            code=404,
            status="NOT_FOUND",
            reason="TASK_NOT_FOUND",
        )
        evidence["http_unsupported_media"] = validate_http_error(
            http.post("/rest/message:send", json=unsupported_request()),
            code=400,
            status="INVALID_ARGUMENT",
            reason=REASON,
        )
        evidence["jsonrpc_unsupported_media"] = validate_jsonrpc_error(
            http.post(
                "/",
                json={
                    "jsonrpc": "2.0",
                    "id": "course-media-check",
                    "method": "SendMessage",
                    "params": unsupported_request(),
                },
            ),
            "course-media-check",
        )
    with grpc.insecure_channel("127.0.0.1:10000") as channel:
        try:
            A2AServiceStub(channel).SendMessage(
                ParseDict(unsupported_request(), SendMessageRequest()),
                metadata=(("a2a-version", "1.0"),),
                timeout=5,
            )
        except grpc.RpcError as error:
            evidence["grpc_unsupported_media"] = validate_grpc_error(
                error.code(),
                error.details(),
                error.trailing_metadata(),
            )
        else:
            raise AssertionError("gRPC accepted an unsupported media type")
    return evidence
