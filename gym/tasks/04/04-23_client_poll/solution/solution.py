from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    task = (await http.post("/message:send", json=as_dict(request(brief)))).json()["task"]
    polled = (await http.get("/tasks/" + task["id"])).json()
    return {"created": task["id"], "polled": polled["id"], "state": polled["status"]["state"]}
