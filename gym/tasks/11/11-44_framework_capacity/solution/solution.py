async def exercise(context):
    from common.protocol import as_dict, request

    response = await context["http"].post(
        context["path"],
        json=as_dict(
            request(
                context["brief"],
                task_id=context.get("task_id", ""),
                context_id=context.get("context_id", ""),
            )
        ),
    )
    return response.text if context["path"].endswith("stream") else response.json()
