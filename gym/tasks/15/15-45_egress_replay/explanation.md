# Why this works

Enforce explicit destinations, public addresses, byte limits and replay protection before accepting external data.

The exercise uses real egress objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.security import verify_webhook

    seen = {}
    verify_webhook(context["body"], context["headers"], context["secret"], seen, now=100)
    try:
        verify_webhook(context["body"], context["headers"], context["secret"], seen, now=100)
        return False
    except ValueError:
        return True
~~~
