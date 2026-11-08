from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    response = await http.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "id": "quote",
            "method": "SendMessage",
            "params": as_dict(request(brief)),
        },
    )
    return response.json()["result"]["task"]
