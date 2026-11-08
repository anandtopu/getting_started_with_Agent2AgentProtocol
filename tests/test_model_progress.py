"""A native provider stream reports safe progress over the actual A2A route."""

import json

import httpx

from agents.app import make_app, make_handler
from agents.langgraph_vendor import LangGraphCatering
from common.config import Settings
from common.lessons import events
from common.llm import Model
from common.protocol import as_dict, request


async def test_native_stream_emits_progress_without_reasoning():
    body = (
        "\n".join(
            json.dumps(p)
            for p in [
                {
                    "message": {
                        "thinking": "PRIVATE REASONING",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "select_action",
                                    "arguments": {"tool": "quote_menu"},
                                }
                            }
                        ],
                    }
                },
                {"done": True, "done_reason": "stop"},
            ]
        )
        + "\n"
    )
    model = Model(
        Settings(llm_provider="ollama", llm_model="offline"),
        httpx.MockTransport(lambda req: httpx.Response(200, text=body)),
    )
    handler = make_handler("catering", executor=LangGraphCatering(model))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=make_app("catering", demo=True, handler=handler)),
        base_url="http://test",
        headers={"A2A-Version": "1.0"},
    ) as client:
        response = await client.post(
            "/message:stream", json=as_dict(request({"guests": 40, "dietary": {"vegan": 40}}))
        )
        assert response.status_code == 200
        assert "Receiving model response" in response.text
        assert "PRIVATE REASONING" not in response.text
        assert (
            events(response.text)[-1]["statusUpdate"]["status"]["state"] == "TASK_STATE_COMPLETED"
        )
    await handler.aclose()
