"""Run all documented experiments for this module."""

from common.lessons import experiment


async def test_examples():
    assert await experiment("parts") is not None
    assert await experiment("rest") is not None
    assert await experiment("ssrf") is not None
