async def exercise(context):
    from common.protocol import as_dict, request

    response = await context["http"].post(
        "/message:send", json=as_dict(request(context["brief"])), headers={}
    )
    return response.status_code
