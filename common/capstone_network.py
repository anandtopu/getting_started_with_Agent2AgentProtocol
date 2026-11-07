"""An offline two-framework network with a scripted planner and real SDK boundaries."""

from contextlib import AsyncExitStack

from agents.app import make_handler
from agents.concierge import Concierge
from agents.langgraph_vendor import LangGraphCatering
from common.fakes import ScriptedModel
from common.testing import client


async def network_lab():
    vendors = ["venues", "catering", "av", "travel", "print"]
    model = ScriptedModel([{"vendors": vendors}])
    menu_model = ScriptedModel([{"tool": "ask_dietary"}, {"tool": "quote_menu"}])
    records = []
    async with AsyncExitStack() as stack:
        clients = {}
        for vendor in vendors:
            handler = (
                make_handler(vendor, executor=LangGraphCatering(menu_model))
                if vendor == "catering"
                else None
            )
            clients[vendor] = await stack.enter_async_context(
                client(vendor, handler=handler, records=records)
            )
        planner = Concierge(clients, model=model)
        brief = {"guests": 40, "budget_cents": 1_000_000}
        first = await planner.plan(brief)
        second = await planner.plan({**brief, "dietary": {"vegan": 40}}, first)
    return {
        "before": first,
        "after": second,
        "model_calls": len(model.calls),
        "wire_exchanges": len(records),
    }
