from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    response = await http.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "SendMessage",
            "params": as_dict(request(brief)),
        },
        headers={"A2A-Version": "99.0"},
    )
    return response.json()["error"]["code"]
