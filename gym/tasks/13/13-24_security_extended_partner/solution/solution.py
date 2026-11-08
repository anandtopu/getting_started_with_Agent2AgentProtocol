async def exercise(http, brief, previous):
    document = (
        await http.get("/extendedAgentCard", headers={"Authorization": "Bearer partner"})
    ).json()
    return next(s["id"] for s in document["skills"] if s["id"] == "travel.partner_quote")
