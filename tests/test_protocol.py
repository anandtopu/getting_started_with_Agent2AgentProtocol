"""Contract tests exercise actual SDK routing, storage, continuation and serialization."""

import json

import pytest
from a2a.types import TaskState

from common.protocol import as_dict, request
from common.testing import InProcessGrpc, client


@pytest.mark.parametrize("vendor", ["venues", "catering", "av", "travel", "print"])
async def test_vendor_quote(vendor):
    async with client(vendor) as http:
        response = await http.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "SendMessage",
                "params": as_dict(
                    request({"guests": 40, "date": "2027-06-01", "dietary": {"vegan": 40}})
                ),
            },
        )
        data = response.json()
        assert "error" not in data, data
        assert data["result"]["task"]["status"]["state"] == "TASK_STATE_COMPLETED", data


async def test_catering_continuation():
    async with client("catering") as http:
        first = (await http.post("/message:send", json=as_dict(request({"guests": 40})))).json()[
            "task"
        ]
        assert first["status"]["state"] == "TASK_STATE_INPUT_REQUIRED"
        next_request = request(
            {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
        )
        second = (await http.post("/message:send", json=as_dict(next_request))).json()["task"]
        assert second["id"] == first["id"]
        assert second["contextId"] == first["contextId"]
        assert second["status"]["state"] == "TASK_STATE_COMPLETED"


async def test_stream_order_and_chunks():
    async with client("av") as http:
        response = await http.post("/message:stream", json=as_dict(request({"guests": 40})))
        events = [
            json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")
        ]
        assert "task" in events[0]
        assert events[-1]["statusUpdate"]["status"]["state"] == "TASK_STATE_COMPLETED"
        chunks = [
            e["artifactUpdate"]
            for e in events
            if "artifactUpdate" in e and e["artifactUpdate"]["artifact"]["artifactId"] == "plan"
        ]
        assert len(chunks) == 3
        assert not chunks[0].get("append", False)
        assert chunks[-1]["append"] and chunks[-1]["lastChunk"]


async def test_grpc_servicer():
    result = await InProcessGrpc().unary("SendMessage", request({"guests": 40}))
    assert result.task.status.state == TaskState.TASK_STATE_COMPLETED
