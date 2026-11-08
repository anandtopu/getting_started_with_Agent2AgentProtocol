# Why this works

Use a typed request and the existing work-order ID.

The exercise uses real grpc objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from a2a.types import CancelTaskRequest
    from common.protocol import as_dict

    return as_dict(
        await context["service"].unary("CancelTask", CancelTaskRequest(id=context["task"].id))
    )
~~~
