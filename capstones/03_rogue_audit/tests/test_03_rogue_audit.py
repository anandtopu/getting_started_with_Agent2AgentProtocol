"""Every planted attack must fail against the hardened boundary."""

from common.audit import audit_lab


async def test_reference_audit():
    result = await audit_lab()
    assert len(result["findings"]) == 6
    assert result["all_attacks_blocked"], result
    assert {f["id"] for f in result["findings"]} == {f"AUD-0{i}" for i in range(1, 7)}
