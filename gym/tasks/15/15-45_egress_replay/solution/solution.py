async def exercise(context):
    from common.security import verify_webhook

    seen = {}
    verify_webhook(context["body"], context["headers"], context["secret"], seen, now=100)
    try:
        verify_webhook(context["body"], context["headers"], context["secret"], seen, now=100)
        return False
    except ValueError:
        return True
