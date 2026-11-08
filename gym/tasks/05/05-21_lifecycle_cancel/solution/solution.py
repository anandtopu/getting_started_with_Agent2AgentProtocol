async def exercise(http, brief, previous):
    return (await http.post("/tasks/" + previous["id"] + ":cancel", json={})).json()
