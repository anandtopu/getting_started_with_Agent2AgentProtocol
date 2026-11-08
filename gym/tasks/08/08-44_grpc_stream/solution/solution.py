async def exercise(context):
    from common.protocol import request

    return [
        event.WhichOneof("payload")
        async for event in context["service"].stream(request(context["brief"]))
    ]
