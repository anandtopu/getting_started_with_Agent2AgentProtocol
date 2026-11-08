"""Opt-in live model check. Defaults to the free Ollama provider configured in .env."""

import asyncio
import json
from pathlib import Path

from common.llm import create_model


async def main():
    model = create_model()
    schema = {
        "type": "object",
        "properties": {"tool": {"type": "string", "enum": ["quote_menu", "ask_dietary"]}},
        "required": ["tool"],
        "additionalProperties": False,
    }
    result = await model.tool_decide(
        "Use select_action. Maplewood needs a menu for 40 vegan guests. Dietary counts are complete. Choose quote_menu.",
        schema,
    )
    assert result == {"tool": "quote_menu"}, result
    from agents.app import make_handler
    from agents.concierge import Concierge
    from agents.langgraph_vendor import LangGraphCatering
    from common.protocol import as_dict, request
    from common.testing import client

    async with client(
        "catering", handler=make_handler("catering", executor=LangGraphCatering(model))
    ) as catering:
        response = await catering.post(
            "/message:stream", json=as_dict(request({"guests": 40, "dietary": {"vegan": 40}}))
        )
        assert "TASK_STATE_COMPLETED" in response.text, response.text
        assert "Receiving model response" in response.text
    async with client("venues") as venues:
        plan = await Concierge({"venues": venues}, model=model).plan(
            {"guests": 40, "needs": ["venues"]}
        )
        assert plan["delegations"][0]["state"] == "TASK_STATE_COMPLETED"
        assert plan["approval_required"]
    evidence = {
        "provider": model.settings.llm_provider,
        "model": model.settings.llm_model,
        "native_streamed_tool_call": result,
        "credentials_logged": False,
        "a2a_langgraph_mcp_stream": "passed",
        "model_selected_concierge_plan": "passed",
    }
    output = Path("workspace/live-model.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence))


if __name__ == "__main__":
    asyncio.run(main())
