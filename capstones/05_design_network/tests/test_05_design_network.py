"""Smoke check of the focused reference slice; see the human rubric."""

from common.hiring import hiring_lab


async def test_reference_slice():
    records = []
    result = await hiring_lab(records)
    first, second = result["before"], result["after"]
    assert first["status"]["state"] == "TASK_STATE_INPUT_REQUIRED"
    assert second["status"]["state"] == "TASK_STATE_COMPLETED"
    assert first["id"] == second["id"]
    artifact = second["artifacts"][0]["parts"][0]["data"]
    assert artifact["hiring_decision"] == "human-review-required"
    background = artifact["delegations"]["background"]["artifacts"][0]["parts"][0]["data"]
    assert background["fixture"] is True
    assert background["decision"] == "human-review-required"
    payloads = [r["request"]["body"]["message"]["parts"][0]["data"] for r in records]
    assert {"consent": False} in payloads and {"consent": True} in payloads
    assert any(set(p) == {"slots"} for p in payloads)
