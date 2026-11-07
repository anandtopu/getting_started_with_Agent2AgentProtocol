"""Compensation is a business operation, not cancellation of a completed A2A task."""

import httpx

from agents.app import make_handler
from agents.holds import HoldExecutor
from common.protocol import as_dict, request
from common.testing import client


async def reserve_pair(travel, venue) -> dict:
    hotel = (await travel.post("/message:send", json=as_dict(request({"action": "hold"})))).json()[
        "task"
    ]
    if hotel["status"]["state"] != "TASK_STATE_COMPLETED":
        return {"reserved": False, "reason": "hotel unavailable", "compensated": False}
    hold_id = hotel["artifacts"][0]["parts"][0]["data"]["hold_id"]
    try:
        room_response = await venue.post("/message:send", json=as_dict(request({"action": "hold"})))
        room_response.raise_for_status()
        room = room_response.json()["task"]
        if room["status"]["state"] == "TASK_STATE_COMPLETED":
            return {
                "reserved": True,
                "hotel_hold": hold_id,
                "venue": room["id"],
                "charged_cents": 0,
            }
    except (httpx.HTTPError, KeyError, ValueError):
        # Cleanup is bounded to the known tentative hold. Its result is checked below.
        room = None
    released = (
        await travel.post(
            "/message:send", json=as_dict(request({"action": "release", "hold_id": hold_id}))
        )
    ).json()["task"]
    compensated = released["status"]["state"] == "TASK_STATE_COMPLETED"
    return {
        "reserved": False,
        "compensated": compensated,
        "manual_followup_required": not compensated,
        "charged_cents": 0,
    }


async def compensation_lab(records=None) -> dict:
    records = records if records is not None else []
    hotel, venue = HoldExecutor("travel"), HoldExecutor("venues", available=False)
    async with client(
        "travel", handler=make_handler("travel", executor=hotel), records=records
    ) as travel:
        async with client(
            "venues", handler=make_handler("venues", executor=venue), records=records
        ) as venues:
            result = await reserve_pair(travel, venues)
            result["remaining_hotel_holds"] = len(hotel.holds)
            return result
