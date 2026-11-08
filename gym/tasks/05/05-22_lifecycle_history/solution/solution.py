from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    follow = request(
        {"dietary": brief["dietary"]}, task_id=previous["id"], context_id=previous["contextId"]
    )
    await http.post("/message:send", json=as_dict(follow))
    return (await http.get("/tasks/" + previous["id"], params={"historyLength": 1})).json()
