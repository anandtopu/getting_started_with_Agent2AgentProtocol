# Why this works

Find the stable skill ID; do not select by free-text instructions.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    card = (await http.get("/.well-known/agent-card.json")).json()
    return next(skill for skill in card["skills"] if skill["id"] == "venues.quote")
~~~
