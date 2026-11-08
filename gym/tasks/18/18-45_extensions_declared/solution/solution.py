async def exercise(context):
    card = (await context["http"].get("/.well-known/agent-card.json")).json()
    return card["capabilities"]["extensions"][0]["uri"]
