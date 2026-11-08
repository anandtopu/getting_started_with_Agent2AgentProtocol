async def exercise(context):
    from common.card_trust import trusted_jwks
    from common.security import verify_card

    ring = context["ring"]
    old = ring.card()
    ring.revoke(ring.current)
    try:
        verify_card(old, trusted_jwks(ring.public_keys()))
        return True
    except ValueError:
        return False
