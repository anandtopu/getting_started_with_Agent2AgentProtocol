"""A resumed five-vendor plan preserves completed work and the planner's scope."""

from common.capstone_network import network_lab


async def test_reference_network():
    result = await network_lab()
    before, after = result["before"]["delegations"], result["after"]["delegations"]
    assert len(after) == 5 and result["model_calls"] == 1
    assert all(item["state"] == "TASK_STATE_COMPLETED" for item in after)
    assert (
        next(item for item in before if item["vendor"] == "catering")["state"]
        == "TASK_STATE_INPUT_REQUIRED"
    )
    for original, resumed in zip(before, after):
        assert original["task_id"] == resumed["task_id"]
        assert original["context_id"] == resumed["context_id"]
    assert result["after"]["approval_required"]
