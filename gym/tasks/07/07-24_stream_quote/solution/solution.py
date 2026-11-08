from common.lessons import events
from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    rows = events((await http.post("/message:stream", json=as_dict(request(brief)))).text)
    return next(
        e["artifactUpdate"]["artifact"]["parts"][0]["data"]
        for e in rows
        if e.get("artifactUpdate", {}).get("artifact", {}).get("artifactId") == "quote"
    )
