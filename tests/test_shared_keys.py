"""A different replica and a process restart must verify cards after rotation."""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from sqlalchemy.ext.asyncio import create_async_engine

from agents.catalog import card
from common.card_trust import trusted_jwks
from common.key_rotation import SharedCardKeys
from common.security import verify_card


async def test_shared_ring_rotation_and_restart(tmp_path):
    url = "sqlite+aiosqlite:///" + (tmp_path / "keys.sqlite").as_posix()
    engines = [create_async_engine(url) for _ in range(2)]
    secret, clock = Ed25519PrivateKey.generate().private_bytes_raw(), [100]
    one, two = [
        SharedCardKeys(card("venues"), e, "venues", secret, clock=lambda: clock[0]) for e in engines
    ]
    try:
        original = (await one.ring()).card()
        verify_card(original, trusted_jwks((await two.ring()).public_keys()))
        clock[0] = 401
        rotated = await two.ring()
        verify_card(original, trusted_jwks((await one.ring()).public_keys()))
        await one.ring(revoke=rotated.current)
        assert (await two.ring()).current != rotated.current
        clock[0] = 500
        import pytest

        with pytest.raises(ValueError):
            verify_card(original, trusted_jwks((await one.ring()).public_keys()))
        restarted = SharedCardKeys(
            card("venues"), engines[0], "venues", secret, clock=lambda: clock[0]
        )
        assert (await restarted.ring()).current == (await two.ring()).current
    finally:
        for engine in engines:
            await engine.dispose()
