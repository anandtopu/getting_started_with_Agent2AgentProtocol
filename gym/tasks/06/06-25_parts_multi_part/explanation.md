# Why this works

Return the structured quote and valid PDF file from the same artifact.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    task = (
        await http.post("/message:send", json=as_dict(request({**brief, "include_files": True})))
    ).json()["task"]
    parts = task["artifacts"][0]["parts"]
    return {
        "data": next(p["data"] for p in parts if "data" in p),
        "file": next(p for p in parts if p.get("mediaType") == "application/pdf"),
    }
~~~
