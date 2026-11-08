async def exercise(context):
    from a2a.server.cluster.task_store import ConcurrentTaskModificationError

    await context["two"].save(
        context["task"],
        event=context["event"],
        prev=None,
        prev_version=context["version"],
        context=context["call"],
    )
    try:
        await context["two"].save(
            context["task"],
            event=context["event"],
            prev=None,
            prev_version=context["version"],
            context=context["call"],
        )
        return False
    except ConcurrentTaskModificationError:
        return True
