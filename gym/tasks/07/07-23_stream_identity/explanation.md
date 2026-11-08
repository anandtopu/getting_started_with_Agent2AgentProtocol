# Why this works

Use the actual snapshot as the identity source and inspect every following event.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    rows = events((await http.post("/message:stream", json=as_dict(request(brief)))).text)

    task = rows[0]["task"]
    updates = [next(iter(e.values())) for e in rows[1:]]
    return {
        "same_task": all(e["taskId"] == task["id"] for e in updates),
        "same_context": all(e["contextId"] == task["contextId"] for e in updates),
        "events": len(rows),
    }
~~~
