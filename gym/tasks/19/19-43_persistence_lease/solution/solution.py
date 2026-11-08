async def exercise(context):
    old = await context["one"].claim(now=100, seconds=5)
    new = await context["two"].claim(now=106)
    return [
        await context["one"].acknowledge(old, True, now=107),
        await context["two"].acknowledge(new, True, now=107),
    ]
