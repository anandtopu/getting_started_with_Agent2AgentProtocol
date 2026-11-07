"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("orchestrate") is not None
    assert await experiment("rejected") is not None
    assert await experiment("compensate") is not None
