"""Opt-in live model check. Defaults to the free Ollama provider configured in .env."""

import asyncio
import json
import sys
from pathlib import Path

import httpx
from jsonschema import ValidationError

from common.llm import create_model

ROOT = Path(__file__).resolve().parents[1]


async def main():
    output = ROOT / "workspace/live-model.json"
    output.unlink(missing_ok=True)
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
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence))


async def run_check():
    try:
        await main()
    except (ValueError, httpx.HTTPError, ValidationError, AssertionError) as exc:
        # Model content and provider diagnostics may contain sensitive input. Do not echo them.
        status = ""
        cause = exc
        while cause is not None:
            if isinstance(cause, httpx.HTTPStatusError):
                status = f" (HTTP {cause.response.status_code})"
                break
            cause = cause.__cause__
        print(
            f"Live-model check failed{status}. Run scripts/check_env.py; check the provider, "
            "model access, private .env credentials and budget, or start Ollama. "
            "See docs/LIVE_MODELS.md. No success report was retained.",
            file=sys.stderr,
        )
        return 1
    return 0


def cli():
    return asyncio.run(run_check())


if __name__ == "__main__":
    raise SystemExit(cli())
