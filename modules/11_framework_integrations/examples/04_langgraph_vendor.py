"""Run Saffron's real LangGraph workflow behind an A2A server.

Concepts: framework adapters, private MCP tools, A2A continuation.
Spec: https://a2a-protocol.org/latest/specification/
Run: uv run python modules/11_framework_integrations/examples/04_langgraph_vendor.py
No running agents or LLM required. Expected: the same task pauses then completes.
"""

import asyncio

from agents.app import make_handler
from agents.langgraph_vendor import LangGraphCatering
from common.fakes import ScriptedModel
from common.pretty import show
from common.protocol import as_dict, request
from common.testing import client


async def main():
    model = ScriptedModel([{"tool": "ask_dietary"}, {"tool": "quote_menu"}])
    handler = make_handler("catering", executor=LangGraphCatering(model))
    async with client("catering", handler=handler) as http:
        first = (await http.post("/message:send", json=as_dict(request({"guests": 40})))).json()[
            "task"
        ]
        # KEY IDEA: framework state stays inside Saffron; A2A carries task/context IDs.
        message = request(
            {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
        )
        second = (await http.post("/message:send", json=as_dict(message))).json()["task"]
        show(
            {
                "before": first["status"]["state"],
                "after": second["status"]["state"],
                "same_task": first["id"] == second["id"],
            }
        )


if __name__ == "__main__":
    asyncio.run(main())
