# Why this works

Resolve securityRequirements through securitySchemes; never treat a card as a credential.

The request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.

## Reference implementation

~~~python
from common.protocol import as_dict, request
from common.lessons import events


async def exercise(http, brief, previous):
    card = (await http.get("/.well-known/agent-card.json")).json()
    required = list(card["securityRequirements"][0]["schemes"])
    return {
        "scheme": card["securitySchemes"][required[0]]["httpAuthSecurityScheme"]["scheme"],
        "required": required,
    }
~~~
