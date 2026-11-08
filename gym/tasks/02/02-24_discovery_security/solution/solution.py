async def exercise(http, brief, previous):
    card = (await http.get("/.well-known/agent-card.json")).json()
    required = list(card["securityRequirements"][0]["schemes"])
    return {
        "scheme": card["securitySchemes"][required[0]]["httpAuthSecurityScheme"]["scheme"],
        "required": required,
    }
