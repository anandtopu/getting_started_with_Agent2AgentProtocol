async def exercise(http, brief, previous):
    return (
        await http.get("/extendedAgentCard", headers={"Authorization": "Bearer owner"})
    ).status_code
