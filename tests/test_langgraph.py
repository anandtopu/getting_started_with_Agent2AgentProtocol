"""Real LangGraph + MCP + A2A with scripted model decisions and no network."""

from agents.app import make_handler
from agents.langgraph_vendor import LangGraphCatering
from common.fakes import ScriptedModel
from common.protocol import as_dict, request
from common.testing import client


async def test_framework_pause_resume_and_quote():
    model = ScriptedModel([{"tool": "quote_menu"}, {"tool": "quote_menu"}])
    async with client(
        "catering", handler=make_handler("catering", executor=LangGraphCatering(model))
    ) as http:
        first = (await http.post("/message:send", json=as_dict(request({"guests": 40})))).json()[
            "task"
        ]
        assert first["status"]["state"] == "TASK_STATE_INPUT_REQUIRED"
        result = (
            await http.post(
                "/message:send",
                json=as_dict(
                    request(
                        {"dietary": {"vegan": 40}},
                        task_id=first["id"],
                        context_id=first["contextId"],
                    )
                ),
            )
        ).json()["task"]
        assert result["id"] == first["id"]
        assert result["status"]["state"] == "TASK_STATE_COMPLETED"
        assert result["artifacts"][0]["parts"][0]["data"]["total_cents"] > 0


async def test_framework_rejects_untrusted_tool_name():
    model = ScriptedModel([{"tool": "send_credentials"}])
    async with client(
        "catering", handler=make_handler("catering", executor=LangGraphCatering(model))
    ) as http:
        result = (await http.post("/message:send", json=as_dict(request({"guests": 40})))).json()[
            "task"
        ]
        assert result["status"]["state"] == "TASK_STATE_FAILED"
        assert not result.get("artifacts")
