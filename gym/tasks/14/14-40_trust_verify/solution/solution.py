async def exercise(context):
    from common.security import verify_card

    return verify_card(context["card"], context["keys"])["name"]
