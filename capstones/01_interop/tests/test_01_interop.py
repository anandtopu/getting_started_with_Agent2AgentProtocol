"""Generated IDs may differ; the task outcome and business artifact must agree."""

from common.interop import interop_lab


async def test_reference_interop():
    result = await interop_lab()
    assert set(result["bindings"]) == {"JSONRPC", "HTTP+JSON", "GRPC"}
    assert result["equivalent"]
    for value in result["bindings"].values():
        assert value["state"] == "TASK_STATE_COMPLETED"
        assert value["quote"]["total_cents"] == 80000
        assert not value["quote"]["approved"]
