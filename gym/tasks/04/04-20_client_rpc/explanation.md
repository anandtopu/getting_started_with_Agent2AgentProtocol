# Why this works

Build the full envelope and return the Task for the supplied brief.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    response = await http.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "id": "quote",
            "method": "SendMessage",
            "params": as_dict(request(brief)),
        },
    )
    return response.json()["result"]["task"]
~~~
