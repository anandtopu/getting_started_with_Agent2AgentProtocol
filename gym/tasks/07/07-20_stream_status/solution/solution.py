from common.lessons import events
from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    rows = events((await http.post("/message:stream", json=as_dict(request(brief)))).text)
    return [
        e["task"]["status"]["state"] if "task" in e else e["statusUpdate"]["status"]["state"]
        for e in rows
        if "task" in e or "statusUpdate" in e
    ]
