async def exercise(context):
    from common.security import verify_card

    try:
        verify_card(context["card"], context["keys"])
        return True
    except ValueError:
        return False
