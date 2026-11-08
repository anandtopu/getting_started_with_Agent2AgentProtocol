from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    return (
        await http.post("/message:send", json=as_dict(request({**brief, "token": "owner"})))
    ).status_code
