from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    response = (
        await http.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": "client-" + str(brief["guests"]),
                "method": "SendMessage",
                "params": as_dict(request(brief)),
            },
        )
    ).json()
    task = response["result"]["task"]
    return {"rpc_id": response["id"], "task_id": task["id"], "context_id": task["contextId"]}
