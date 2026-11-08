async def exercise(context):
    from common.protocol import as_dict, request

    return (
        await context["http"].post("/message:send", json=as_dict(request(context["brief"])))
    ).json()
