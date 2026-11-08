from common.lessons import events
from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    rows = events((await http.post("/message:stream", json=as_dict(request(brief)))).text)

    text = ""
    for event in rows:
        update = event.get("artifactUpdate", {})
        if update.get("artifact", {}).get("artifactId") == "plan":
            chunk = "".join(p.get("text", "") for p in update["artifact"]["parts"])
            text = text + chunk if update.get("append", False) else chunk
    return text
