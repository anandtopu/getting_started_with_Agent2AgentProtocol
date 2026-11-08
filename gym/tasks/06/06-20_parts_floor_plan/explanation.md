# Why this works

Return the raw SVG image Part, preserving its filename and media type.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    task = (
        await http.post("/message:send", json=as_dict(request({**brief, "include_files": True})))
    ).json()["task"]
    return next(
        p for a in task["artifacts"] for p in a["parts"] if p.get("mediaType") == "image/svg+xml"
    )
~~~
