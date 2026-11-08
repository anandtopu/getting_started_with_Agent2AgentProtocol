from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    task = (
        await http.post("/message:send", json=as_dict(request({**brief, "include_files": True})))
    ).json()["task"]
    return sorted(a["artifactId"] for a in task["artifacts"])
