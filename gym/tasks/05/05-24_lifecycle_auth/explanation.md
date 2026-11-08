# Why this works

Ask for a partner-only action. Observe auth-required without placing a credential in the message.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    return (
        await http.post("/message:send", json=as_dict(request({**brief, "require_partner": True})))
    ).json()["task"]
~~~
