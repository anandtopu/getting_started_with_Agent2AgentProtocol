async def exercise(http, brief, previous):
    response = await http.post(
        "/rpc", json={"jsonrpc": "2.0", "id": 1, "method": "InventedOperation", "params": {}}
    )
    return response.json()["error"]["code"]
