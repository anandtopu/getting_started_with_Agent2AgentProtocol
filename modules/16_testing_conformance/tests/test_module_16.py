"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("errors") is not None
    assert await experiment("stream") is not None
    assert await experiment("grpc") is not None
