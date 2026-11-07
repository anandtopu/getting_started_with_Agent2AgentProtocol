"""A scripted model selects verified skills; real A2A calls produce the quotes.

Concepts: SendMessage, skill discovery, bounded delegation. Spec: A2A 1.0.1.
Run: uv run python modules/10_orchestrator/examples/04_model_selection.py.
No running agents or model needed. Expected: venues completed; approval_required true.
"""

import asyncio

from agents.concierge import Concierge
from common.fakes import ScriptedModel
from common.pretty import show
from common.testing import client


async def main():
    model = ScriptedModel([{"vendors": ["venues"]}])
    async with client("venues") as venue:
        # KEY IDEA: the model selects a known capability; deterministic code owns money.
        show(await Concierge({"venues": venue}, model=model).plan({"guests": 40}))


if __name__ == "__main__":
    asyncio.run(main())
