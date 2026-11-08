from common.lessons import events
from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    rows = events((await http.post("/message:stream", json=as_dict(request(brief)))).text)

    task = rows[0]["task"]
    updates = [next(iter(e.values())) for e in rows[1:]]
    return {
        "same_task": all(e["taskId"] == task["id"] for e in updates),
        "same_context": all(e["contextId"] == task["contextId"] for e in updates),
        "events": len(rows),
    }
