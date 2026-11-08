async def exercise(http, brief, previous):
    card = (await http.get("/.well-known/agent-card.json")).json()
    return card["defaultInputModes"]
