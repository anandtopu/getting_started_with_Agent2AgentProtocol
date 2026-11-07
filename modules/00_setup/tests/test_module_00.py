"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("discover") is not None
    assert await experiment("data") is not None
    assert await experiment("jsonrpc") is not None
