# Why this works

Discover first, then configure the SDK client with the provided authenticated transport.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    from a2a.client import ClientConfig, create_client
    from a2a.types import AgentCard
    from google.protobuf.json_format import ParseDict

    card = ParseDict((await http.get("/.well-known/agent-card.json")).json(), AgentCard())
    sdk = await create_client(card, ClientConfig(httpx_client=http, streaming=False))
    result = [as_dict(item) async for item in sdk.send_message(request(brief))][-1]
    return result["task"]
~~~
