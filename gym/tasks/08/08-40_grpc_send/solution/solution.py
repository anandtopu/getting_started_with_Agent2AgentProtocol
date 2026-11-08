async def exercise(context):
    from common.protocol import as_dict, request

    return as_dict(await context["service"].unary("SendMessage", request(context["brief"])))
