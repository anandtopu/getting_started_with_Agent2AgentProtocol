"""Each normative operation has an actual captured call in every binding."""

import json

import pytest
from a2a.types import a2a_pb2

from common.config import ROOT


@pytest.mark.parametrize("binding", ["jsonrpc", "http_json", "grpc"])
def test_complete_operation_captures(binding):
    rows = [
        json.loads(line)
        for line in (ROOT / f"docs/wire/{binding}-operations.jsonl").read_text().splitlines()
    ]
    methods = {m.name for m in a2a_pb2.DESCRIPTOR.services_by_name["A2AService"].methods}
    assert len(rows) == len(methods)
    if binding == "grpc":
        assert {r["operation"] for r in rows} == methods
        assert [
            r["operation"]
            for r in rows
            if isinstance(r["response"], dict) and "error" in r["response"]
        ] == ["SubscribeToTask"]
    elif binding == "jsonrpc":
        assert {r["request"]["body"]["method"] for r in rows} == methods
        errors = [
            r
            for r in rows
            if isinstance(r["response"]["body"], dict) and "error" in r["response"]["body"]
        ]
        assert len(errors) == 1 and errors[0]["request"]["body"]["method"] == "SubscribeToTask"
    else:
        errors = [r for r in rows if r["response"]["status"] >= 400]
        assert len(errors) == 1 and errors[0]["request"]["url"].endswith(":subscribe")
