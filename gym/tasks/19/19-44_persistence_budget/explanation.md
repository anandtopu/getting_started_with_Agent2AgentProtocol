# Why this works

Two replicas together must allow only three requests in the same fixed window.

The exercise uses real persistence objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    accepted = 0
    for index in range(8):
        store = context["one"] if index % 2 else context["two"]
        accepted += await store.allow("maplewood:planner", now=100, limit=3)
    return accepted
~~~
