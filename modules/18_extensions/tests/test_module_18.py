"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("extension") is not None
    assert await experiment("version") is not None
    assert await experiment("list") is not None
