async def exercise(context):
    from a2a.types import CancelTaskRequest

    from common.protocol import as_dict

    return as_dict(
        await context["service"].unary("CancelTask", CancelTaskRequest(id=context["task"].id))
    )
