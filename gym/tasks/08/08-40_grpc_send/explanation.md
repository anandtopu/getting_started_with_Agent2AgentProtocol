# Why this works

Use the official gRPC service with the supplied brief; return ProtoJSON for inspection.

The exercise uses real grpc objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.protocol import request, as_dict

    return as_dict(await context["service"].unary("SendMessage", request(context["brief"])))
~~~
