"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("stream") is not None
    assert await experiment("chunks") is not None
    assert await experiment("push") is not None
