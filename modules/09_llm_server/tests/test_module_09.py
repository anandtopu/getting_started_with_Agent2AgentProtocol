"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("fake_llm") is not None
    assert await experiment("tool_call") is not None
    assert await experiment("tool_budget") is not None
