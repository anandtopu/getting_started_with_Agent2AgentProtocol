async def exercise(context):
    accepted = 0
    for index in range(8):
        store = context["one"] if index % 2 else context["two"]
        accepted += await store.allow("maplewood:planner", now=100, limit=3)
    return accepted
