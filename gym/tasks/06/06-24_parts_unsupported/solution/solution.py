from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    message = as_dict(request(brief))
    message["message"]["parts"][0]["mediaType"] = "application/x-private-format"
    return (await http.post("/message:send", json=message)).status_code
