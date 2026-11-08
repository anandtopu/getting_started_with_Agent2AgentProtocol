from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    for _ in range(2):
        await http.post("/message:send", json=as_dict(request(brief)))
    return (await http.get("/tasks", params={"pageSize": 1})).json()
