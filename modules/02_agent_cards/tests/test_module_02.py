"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("discover") is not None
    assert await experiment("validate_card") is not None
    assert await experiment("registry") is not None
