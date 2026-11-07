"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("delegate") is not None
    assert await experiment("grpc") is not None
    assert await experiment("eval") is not None
