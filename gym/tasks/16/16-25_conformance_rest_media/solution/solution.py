async def exercise(http, brief, previous):
    return (await http.get("/tasks/never-created")).headers["content-type"]
