# Why this works

Write once, then retry with the old version token and detect the conflict.

The exercise uses real persistence objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from a2a.server.cluster.task_store import ConcurrentTaskModificationError

    await context["two"].save(
        context["task"],
        event=context["event"],
        prev=None,
        prev_version=context["version"],
        context=context["call"],
    )
    try:
        await context["two"].save(
            context["task"],
            event=context["event"],
            prev=None,
            prev_version=context["version"],
            context=context["call"],
        )
        return False
    except ConcurrentTaskModificationError:
        return True
~~~
