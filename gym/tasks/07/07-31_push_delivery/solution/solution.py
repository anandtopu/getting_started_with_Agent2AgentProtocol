from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    message = request(brief, task_id=previous["id"], context_id=previous["contextId"])
    return (await http.post("/message:send", json=as_dict(message))).json()["task"]
