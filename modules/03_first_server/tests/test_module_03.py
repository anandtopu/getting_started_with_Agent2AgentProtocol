"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("rest") is not None
    assert await experiment("stream") is not None
    assert await experiment("rejected") is not None
