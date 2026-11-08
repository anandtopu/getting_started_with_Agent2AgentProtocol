# Why this works

Observe negotiation at the A2A request boundary; the card declaration alone does not activate an extension.

The exercise uses real extensions objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.protocol import request, as_dict

    response = await context["http"].post(
        "/message:send",
        json=as_dict(request(context["brief"])),
        headers={"A2A-Extensions": context["extension"]},
    )
    return response.json()["task"]["artifacts"][0].get("extensions", [])
~~~
