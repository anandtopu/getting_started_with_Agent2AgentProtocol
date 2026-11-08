async def exercise(context):
    from agents.concierge import Concierge

    try:
        return await Concierge(
            context["clients"], model=context.get("model"), fallbacks=context.get("fallbacks")
        ).plan(context["brief"], context.get("previous"))
    except ValueError:
        return {"rejected_selection": True}
