from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    task = (
        await http.post("/message:send", json=as_dict(request({**brief, "include_files": True})))
    ).json()["task"]
    parts = task["artifacts"][0]["parts"]
    return {
        "data": next(p["data"] for p in parts if "data" in p),
        "file": next(p for p in parts if p.get("mediaType") == "application/pdf"),
    }
