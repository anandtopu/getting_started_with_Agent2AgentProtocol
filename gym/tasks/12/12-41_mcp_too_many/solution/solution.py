async def exercise(context):
    from agents.kitchen import check_kitchen

    try:
        return await check_kitchen(context["guests"])
    except ValueError:
        return {"rejected": True}
