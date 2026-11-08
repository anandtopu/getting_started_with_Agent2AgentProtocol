async def exercise(context):
    from a2a.types import ListTasksRequest

    from common.protocol import as_dict

    return as_dict(await context["service"].unary("ListTasks", ListTasksRequest(page_size=1)))
