from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    task = (
        await http.post("/message:send", json=as_dict(request({**brief, "include_files": True})))
    ).json()["task"]
    return next(
        p for a in task["artifacts"] for p in a["parts"] if p.get("mediaType") == "image/svg+xml"
    )
