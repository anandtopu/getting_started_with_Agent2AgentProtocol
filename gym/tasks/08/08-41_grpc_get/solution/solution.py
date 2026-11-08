async def exercise(context):
    from a2a.types import GetTaskRequest

    from common.protocol import as_dict

    return as_dict(await context["service"].unary("GetTask", GetTaskRequest(id=context["task"].id)))
