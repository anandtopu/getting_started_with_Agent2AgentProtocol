from common.protocol import as_dict, request


async def resume(http, first):
    message = request(
        {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
    )
    return (await http.post("/message:send", json=as_dict(message))).json()["task"]
