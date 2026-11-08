# Why this works

Identify the initial Task and final status update without assuming SSE framing.

The exercise uses real grpc objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.protocol import request

    return [
        event.WhichOneof("payload")
        async for event in context["service"].stream(request(context["brief"]))
    ]
~~~
