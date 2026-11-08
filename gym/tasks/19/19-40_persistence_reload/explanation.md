# Why this works

Read the committed task from an independent database connection.

The exercise uses real persistence objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    return (await context["two"].get(context["task"].id, context["call"])).task.id
~~~
