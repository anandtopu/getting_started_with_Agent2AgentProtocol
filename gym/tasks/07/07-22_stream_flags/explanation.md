# Why this works

Return append/lastChunk pairs for the three plan chunks; task completion is separate.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    rows = events((await http.post("/message:stream", json=as_dict(request(brief)))).text)
    return [
        [e["artifactUpdate"].get("append", False), e["artifactUpdate"].get("lastChunk", False)]
        for e in rows
        if e.get("artifactUpdate", {}).get("artifact", {}).get("artifactId") == "plan"
    ]
~~~
