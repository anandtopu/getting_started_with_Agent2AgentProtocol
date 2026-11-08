async def exercise(context):
    response = await context["http"].post("/rpc", **context["arguments"])
    return response.json()
