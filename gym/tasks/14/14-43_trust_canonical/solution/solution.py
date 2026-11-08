async def exercise(context):
    from common.security import sign_card

    document = dict(reversed(list(context["card"].items())))
    return sign_card(document, context["private"], context["kid"])
