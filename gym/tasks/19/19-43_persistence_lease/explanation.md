# Why this works

Only the current lease holder may acknowledge a delivery after recovery.

The exercise uses real persistence objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    old = await context["one"].claim(now=100, seconds=5)
    new = await context["two"].claim(now=106)
    return [
        await context["one"].acknowledge(old, True, now=107),
        await context["two"].acknowledge(new, True, now=107),
    ]
~~~
