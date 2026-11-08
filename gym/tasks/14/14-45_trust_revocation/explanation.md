# Why this works

A previously valid card must fail once its signing key is revoked.

The exercise uses real trust objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.security import verify_card
    from common.card_trust import trusted_jwks

    ring = context["ring"]
    old = ring.card()
    ring.revoke(ring.current)
    try:
        verify_card(old, trusted_jwks(ring.public_keys()))
        return True
    except ValueError:
        return False
~~~
