async def exercise(context):
    from common.protocol import as_dict, request

    response = await context["http"].post(
        "/message:send",
        json=as_dict(request(context["brief"])),
        headers={"A2A-Extensions": context["extension"]},
    )
    return response.status_code
