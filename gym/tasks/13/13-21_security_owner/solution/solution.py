async def exercise(http, brief, previous):
    return (
        await http.get("/tasks/" + previous["id"], headers={"Authorization": "Bearer stranger"})
    ).status_code
