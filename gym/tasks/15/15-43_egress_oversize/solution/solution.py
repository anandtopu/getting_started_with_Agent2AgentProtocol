async def exercise(context):
    from common.security import fetch_file

    try:
        return await fetch_file(context["url"], context["allowed"], context["http"], limit=64)
    except ValueError:
        return None
