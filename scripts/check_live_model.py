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
    evidence = {
        "provider": model.settings.llm_provider,
        "model": model.settings.llm_model,
        "native_streamed_tool_call": result,
        "credentials_logged": False,
    }
    output = Path("workspace/live-model.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence))


if __name__ == "__main__":
    asyncio.run(main())
