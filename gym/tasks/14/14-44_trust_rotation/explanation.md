# Why this works

Accept the old signature during overlap and reject it after retirement.

The exercise uses real trust objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.security import verify_card
    from common.card_trust import trusted_jwks

    ring, clock = context["ring"], context["clock"]
    old = ring.card()
    clock[0] = 101
    verify_card(old, trusted_jwks(ring.public_keys()))
    clock[0] = 132
    try:
        verify_card(old, trusted_jwks(ring.public_keys()))
        expired = True
    except ValueError:
        expired = False
    return {"overlap": True, "expired": expired}
~~~
