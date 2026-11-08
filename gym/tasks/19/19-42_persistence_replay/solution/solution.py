async def exercise(context):
    from a2a.server.cluster.version import TaskVersion

    stream = context["two"].subscribe(context["task"].id, after=TaskVersion.MISSING)
    try:
        return (await anext(stream)).event.task_id
    finally:
        await stream.aclose()
