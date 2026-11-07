"""No-charge holds are released after downstream failure; release is idempotent."""

from agents.app import make_handler
from agents.holds import HoldExecutor
from common.protocol import as_dict, request
from common.saga import compensation_lab
from common.testing import client


async def test_venue_failure_releases_hotel():
    result = await compensation_lab()
    assert not result["reserved"] and result["compensated"]
    assert result["remaining_hotel_holds"] == result["charged_cents"] == 0
    assert not result["manual_followup_required"]


async def test_repeated_release_is_safe():
    executor = HoldExecutor("travel")
    async with client("travel", handler=make_handler("travel", executor=executor)) as http:
        task = (await http.post("/message:send", json=as_dict(request({"action": "hold"})))).json()[
            "task"
        ]
        hold_id = task["artifacts"][0]["parts"][0]["data"]["hold_id"]
        for _ in range(2):
            task = (
                await http.post(
                    "/message:send",
                    json=as_dict(request({"action": "release", "hold_id": hold_id})),
                )
            ).json()["task"]
            assert task["status"]["state"] == "TASK_STATE_COMPLETED"
        assert not executor.holds
