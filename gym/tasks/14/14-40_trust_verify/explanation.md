# Why this works

Verify cryptographic integrity before accepting the vendor identity.

The exercise uses real trust objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.security import verify_card

    return verify_card(context["card"], context["keys"])["name"]
~~~
