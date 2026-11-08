from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    body = as_dict(request(brief))
    body["message"]["parts"][0]["mediaType"] = "application/x-unsupported-tck-type"
    response = await http.post(
        "/rpc", json={"jsonrpc": "2.0", "id": 1, "method": "SendMessage", "params": body}
    )
    return response.json()["error"]["code"]
