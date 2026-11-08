# Why this works

Read the extension URI from the public card and preserve its versioned identity.

The exercise uses real extensions objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    card = (await context["http"].get("/.well-known/agent-card.json")).json()
    return card["capabilities"]["extensions"][0]["uri"]
~~~
