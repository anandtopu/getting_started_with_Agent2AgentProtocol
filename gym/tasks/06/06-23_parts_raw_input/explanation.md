# Why this works

Send a data Part and an inline raw Part in one message using protobuf serialization.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    from a2a.types import Part

    message = request(brief)
    message.message.parts.append(
        Part(
            raw=b"synthetic-artwork", filename="artwork.bin", media_type="application/octet-stream"
        )
    )
    return (await http.post("/message:send", json=as_dict(message))).json()["task"]
~~~
