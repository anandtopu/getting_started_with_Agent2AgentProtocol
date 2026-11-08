from common.lessons import events
from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    rows = events((await http.post("/message:stream", json=as_dict(request(brief)))).text)

    task = (await http.get("/tasks/" + rows[0]["task"]["id"])).json()
    return {
        "state": task["status"]["state"],
        "artifact_ids": sorted(a["artifactId"] for a in task["artifacts"]),
    }
