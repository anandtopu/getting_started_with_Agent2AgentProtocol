"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("pause") is not None
    assert await experiment("resume") is not None
    assert await experiment("cancel") is not None
