from common.protocol import as_dict, request


async def resume(http, first):
    # YOUR CODE HERE: connect this follow-up to the paused task.
    message = request({"dietary": {"vegan": 40}})
    return (await http.post("/message:send", json=as_dict(message))).json()["task"]
