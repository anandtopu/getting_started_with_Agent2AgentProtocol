async def exercise(context):
    from agents.catalog import card

    identity = card("print", grpc_only=True)
    interface = next(i for i in identity.supported_interfaces if i.protocol_binding == "GRPC")
    return interface.protocol_version
