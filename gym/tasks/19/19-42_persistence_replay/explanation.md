# Why this works

Read the durable journal even though the first replica never called publish.

The exercise uses real persistence objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from a2a.server.cluster.version import TaskVersion

    stream = context["two"].subscribe(context["task"].id, after=TaskVersion.MISSING)
    try:
        return (await anext(stream)).event.task_id
    finally:
        await stream.aclose()
~~~
