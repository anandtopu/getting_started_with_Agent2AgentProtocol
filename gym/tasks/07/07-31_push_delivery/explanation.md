# Why this works

Resume the paused task. The durable kit must deliver a signed completion callback to its verified receiver.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    message = request(brief, task_id=previous["id"], context_id=previous["contextId"])
    return (await http.post("/message:send", json=as_dict(message))).json()["task"]
~~~
