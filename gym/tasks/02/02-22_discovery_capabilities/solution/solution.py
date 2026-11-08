async def exercise(http, brief, previous):
    card = (await http.get("/.well-known/agent-card.json")).json()
    cap = card["capabilities"]
    return {
        "streaming": cap.get("streaming", False),
        "push": cap.get("pushNotifications", False),
        "extended": cap.get("extendedAgentCard", False),
    }
