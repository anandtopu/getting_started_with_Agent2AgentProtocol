"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("tool_call") is not None
    assert await experiment("delegate") is not None
    assert await experiment("parts") is not None
