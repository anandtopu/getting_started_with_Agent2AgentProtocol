"""The MCP tool is real; both protocol transports stay in memory."""

from agents.app import make_handler
from agents.kitchen import check_kitchen
from agents.mcp_executor import KitchenExecutor
from common.protocol import as_dict, request
from common.testing import client


async def test_kitchen_tool():
    result = await check_kitchen(40)
    assert result["available"] and result["capacity"] == 300


async def test_mcp_behind_a2a():
    async with client(
        "catering", handler=make_handler("catering", executor=KitchenExecutor())
    ) as http:
        response = await http.post(
            "/message:send", json=as_dict(request({"guests": 40, "dietary": {"vegan": 40}}))
        )
        task = response.json()["task"]
        assert task["status"]["state"] == "TASK_STATE_COMPLETED"
        assert task["artifacts"][0]["parts"][0]["data"]["vendor"] == "catering"
        rejected = await http.post("/message:send", json=as_dict(request({"guests": 400})))
        assert rejected.json()["task"]["status"]["state"] == "TASK_STATE_REJECTED"
