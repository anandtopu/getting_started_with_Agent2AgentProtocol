"""Mutation controls for the TCK exceptions: malformed evidence must stay red."""

import copy
import xml.etree.ElementTree as ET
from unittest.mock import Mock

import grpc
import httpx
import pytest
from google.protobuf.any_pb2 import Any
from google.rpc import error_details_pb2, status_pb2

from scripts.check_tck import (
    EXPECTED_CASES,
    KNOWN_FAILURES,
    expected_failure,
    is_known_failure,
    report_problems,
    wait_for_fixture,
)
from scripts.tck_evidence import (
    ERROR_INFO,
    REASON,
    validate_grpc_error,
    validate_http_error,
    validate_jsonrpc_error,
)


def report():
    root = ET.Element("testsuites")
    suite = ET.SubElement(
        root, "testsuite", tests=str(EXPECTED_CASES), failures="4", errors="0", skipped="57"
    )
    for name in KNOWN_FAILURES:
        classname, message = expected_failure(name)
        case = ET.SubElement(suite, "testcase", classname=classname, name=name)
        ET.SubElement(case, "failure", message=message)
    for index in range(EXPECTED_CASES - 4):
        case = ET.SubElement(suite, "testcase", classname="fixture", name=str(index))
        if index < 57:
            ET.SubElement(case, "skipped")
    return root, suite


def test_baseline_and_genuine_fixes_pass():
    root, suite = report()
    assert not report_problems(root, 1)
    for case in list(suite)[:4]:
        assert is_known_failure(case)
        case.remove(case.find("failure"))
    suite.set("failures", "0")
    assert not report_problems(root, 0)


@pytest.mark.parametrize("name", KNOWN_FAILURES)
@pytest.mark.parametrize(
    "mutation",
    ["additional_error", "wrong_class", "duplicate_failure", "error", "skipped", "changed_code"],
)
def test_exception_match_is_exact(name, mutation):
    classname, message = expected_failure(name)
    case = ET.Element("testcase", classname=classname, name=name)
    failure = ET.SubElement(case, "failure", message=message)
    if mutation == "additional_error":
        failure.set("message", message + "; error domain is invalid")
    elif mutation == "wrong_class":
        case.set("classname", "unreviewed.test")
    elif mutation == "duplicate_failure":
        ET.SubElement(case, "failure", message=message)
    elif mutation in ("error", "skipped"):
        ET.SubElement(case, mutation)
    else:
        failure.set(
            "message",
            message.replace("application/a2a+json", "text/plain").replace(
                "Operation failed:", "Operation failed with INTERNAL:"
            ),
        )
    assert not is_known_failure(case)


@pytest.mark.parametrize(
    "mutation",
    [
        "partial",
        "duplicate",
        "counter",
        "skip",
        "error",
        "wrong_exit",
        "missing_obligation",
        "new_failure",
    ],
)
def test_invalid_reports_fail_closed(mutation):
    root, suite = report()
    returncode = 1
    if mutation == "partial":
        suite.remove(suite[-1])
        suite.set("tests", str(EXPECTED_CASES - 1))
    elif mutation == "duplicate":
        suite[-1].attrib.update(suite[-2].attrib)
    elif mutation == "counter":
        suite.set("failures", "3")
    elif mutation == "skip":
        ET.SubElement(suite[-1], "skipped")
        suite.set("skipped", "58")
    elif mutation == "error":
        ET.SubElement(suite[-1], "error")
        suite.set("errors", "1")
    elif mutation == "wrong_exit":
        returncode = 0
    elif mutation == "missing_obligation":
        suite[0].set("name", "different_check")
        suite[0].remove(suite[0].find("failure"))
        suite.set("failures", "3")
    else:
        ET.SubElement(suite[-1], "failure", message="new regression")
        suite.set("failures", "5")
    assert report_problems(root, returncode)


def test_fixture_readiness_times_out(monkeypatch):
    client = Mock()
    client.get.return_value = httpx.Response(200, json={"name": "unrelated service"})
    context = Mock()
    context.__enter__ = Mock(return_value=client)
    context.__exit__ = Mock(return_value=False)
    monkeypatch.setattr("scripts.check_tck.httpx.Client", Mock(return_value=context))
    monkeypatch.setattr("scripts.check_tck.time.sleep", lambda _: None)
    with pytest.raises(RuntimeError, match="did not become ready"):
        wait_for_fixture(Mock(poll=Mock(return_value=None)))
    assert client.get.call_count == 60


def http_error():
    return {
        "error": {
            "code": 400,
            "status": "INVALID_ARGUMENT",
            "message": "Rejected media",
            "details": [{"@type": ERROR_INFO, "reason": REASON, "domain": "a2a-protocol.org"}],
        }
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "status",
        "code",
        "reason",
        "domain",
        "type",
        "details",
        "content_type",
        "http_status",
        "message",
    ],
)
def test_http_wire_control_rejects_incorrect_errors(mutation):
    body = http_error()
    code, content_type = 400, "application/a2a+json"
    if mutation in ("status", "code", "details", "message"):
        body["error"][mutation] = None
    elif mutation in ("reason", "domain", "type"):
        body["error"]["details"][0]["@type" if mutation == "type" else mutation] = "incorrect"
    elif mutation == "content_type":
        content_type = "application/json"
    else:
        code = 500
    with pytest.raises(AssertionError):
        validate_http_error(
            httpx.Response(code, json=body, headers={"content-type": content_type}),
            code=400,
            status="INVALID_ARGUMENT",
            reason=REASON,
        )


def grpc_status():
    info = error_details_pb2.ErrorInfo(reason=REASON, domain="a2a-protocol.org")
    detail = Any()
    detail.Pack(info)
    return status_pb2.Status(code=3, message="Rejected media", details=[detail])


@pytest.mark.parametrize(
    "mutation", ["status", "message", "reason", "domain", "details", "trailer"]
)
def test_grpc_wire_control_rejects_incorrect_errors(mutation):
    status = grpc_status()
    if mutation == "status":
        status.code = 13
    elif mutation == "message":
        status.message = "Different error"
    elif mutation in ("reason", "domain"):
        info = error_details_pb2.ErrorInfo(reason=REASON, domain="a2a-protocol.org")
        setattr(info, mutation, "incorrect")
        status.details[0].Pack(info)
    elif mutation == "details":
        status.ClearField("details")
    trailers = (
        [] if mutation == "trailer" else [("grpc-status-details-bin", status.SerializeToString())]
    )
    with pytest.raises(AssertionError):
        validate_grpc_error(grpc.StatusCode.INVALID_ARGUMENT, "Rejected media", trailers)


def test_jsonrpc_wire_control_rejects_wrong_code_or_success():
    body = {"jsonrpc": "2.0", "id": "test", "error": {"code": -32005, "message": "Rejected media"}}
    assert validate_jsonrpc_error(httpx.Response(200, json=body), "test") == body
    for field, value in (("code", -32603), ("message", "")):
        changed = copy.deepcopy(body)
        changed["error"][field] = value
        with pytest.raises(AssertionError):
            validate_jsonrpc_error(httpx.Response(200, json=changed), "test")
    body["result"] = {}
    with pytest.raises(AssertionError):
        validate_jsonrpc_error(httpx.Response(200, json=body), "test")


def test_jsonrpc_wire_control_validates_present_details():
    body = {
        "jsonrpc": "2.0",
        "id": "test",
        "error": {
            "code": -32005,
            "message": "Rejected media",
            "data": http_error()["error"]["details"],
        },
    }
    assert validate_jsonrpc_error(httpx.Response(200, json=body), "test")
    body["error"]["data"][0]["domain"] = "incorrect"
    with pytest.raises(AssertionError):
        validate_jsonrpc_error(httpx.Response(200, json=body), "test")


def test_valid_rich_errors_pass():
    assert validate_http_error(
        httpx.Response(400, json=http_error(), headers={"content-type": "application/a2a+json"}),
        code=400,
        status="INVALID_ARGUMENT",
        reason=REASON,
    )
    status = grpc_status()
    assert validate_grpc_error(
        grpc.StatusCode.INVALID_ARGUMENT,
        status.message,
        [("grpc-status-details-bin", status.SerializeToString())],
    )
