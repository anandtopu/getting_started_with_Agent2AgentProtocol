"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("sign") is not None
    assert await experiment("forgery") is not None
    assert await experiment("jwks") is not None
