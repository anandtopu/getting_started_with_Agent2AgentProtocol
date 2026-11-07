"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("sdk_client") is not None
    assert await experiment("rest") is not None
    assert await experiment("errors") is not None
