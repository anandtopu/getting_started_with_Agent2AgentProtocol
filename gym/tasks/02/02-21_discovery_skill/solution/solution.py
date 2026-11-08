async def exercise(http, brief, previous):
    card = (await http.get("/.well-known/agent-card.json")).json()
    return next(skill for skill in card["skills"] if skill["id"] == "venues.quote")
