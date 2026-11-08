async def exercise(context):
    return (await context["two"].get(context["task"].id, context["call"])).task.id
