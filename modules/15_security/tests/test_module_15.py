"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("ssrf") is not None
    assert await experiment("forgery") is not None
    assert await experiment("minimize") is not None
