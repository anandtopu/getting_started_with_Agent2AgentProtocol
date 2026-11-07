"""Smoke check of the focused reference slice; see the human rubric."""

from common.vendor_kit import kit_lab


async def test_reference_slice():
    result = await kit_lab()
    assert result["signature_verified"] and result["unauthorized_status"] == 401
    assert result["before"] == "TASK_STATE_INPUT_REQUIRED"
    assert result["stream"][-1]["statusUpdate"]["status"]["state"] == "TASK_STATE_COMPLETED"
    assert result["verified_push_deliveries"]
