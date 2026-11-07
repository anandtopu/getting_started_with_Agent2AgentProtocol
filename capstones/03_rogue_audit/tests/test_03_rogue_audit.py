"""Smoke check of the focused reference slice; see the human rubric."""

from common.lessons import experiment


async def test_reference_slice():
    result = await experiment("forgery")
    assert isinstance(result, dict)
    assert result
