"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("auth") is not None
    assert await experiment("extended") is not None
    assert await experiment("pause") is not None
