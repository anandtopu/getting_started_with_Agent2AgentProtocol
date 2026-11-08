async def exercise(context):
    from common.card_trust import trusted_jwks
    from common.security import verify_card

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
