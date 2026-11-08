# Why this works

Read the advertised wire version instead of using the SDK package version.

The exercise uses real grpc objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from agents.catalog import card

    identity = card("print", grpc_only=True)
    interface = next(i for i in identity.supported_interfaces if i.protocol_binding == "GRPC")
    return interface.protocol_version
~~~
