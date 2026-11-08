"""Compensation is a business operation, not cancellation of a completed A2A task."""

import httpx

from agents.app import make_handler
from agents.holds import HoldExecutor
from common.protocol import as_dict, request
from common.testing import client


async def reserve_pair(travel, venue, request_id="introductory-hold") -> dict:
    try:
        hotel_response = await travel.post(
            "/message:send",
            json=as_dict(request({"action": "hold", "request_id": request_id + ":hotel"})),
        )
        hotel_response.raise_for_status()
        hotel = hotel_response.json()["task"]
        if hotel["status"]["state"] != "TASK_STATE_COMPLETED":
            return {"reserved": False, "reason": "hotel unavailable", "compensated": False}
        hold_id = hotel["artifacts"][0]["parts"][0]["data"]["hold_id"]
        if not isinstance(hold_id, str) or not hold_id:
            raise ValueError("Hotel confirmation has no hold identifier")
    except (httpx.HTTPError, KeyError, ValueError, TypeError, IndexError):
        recovered = False
        try:
            cleanup = await travel.post(
                "/message:send",
                json=as_dict(
                    request({"action": "release_request", "request_id": request_id + ":hotel"})
                ),
            )
            cleanup.raise_for_status()
            recovered = cleanup.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
        except (httpx.HTTPError, KeyError, ValueError, TypeError, IndexError):
            pass
        return {
            "reserved": False,
            "compensated": recovered,
            "manual_followup_required": not recovered,
            "charged_cents": 0,
        }
    uncertain_cleanup = True
    try:
        room_response = await venue.post(
            "/message:send",
            json=as_dict(request({"action": "hold", "request_id": request_id + ":venue"})),
        )
        room_response.raise_for_status()
        room = room_response.json()["task"]
        if room["status"]["state"] == "TASK_STATE_COMPLETED":
            venue_hold = room["artifacts"][0]["parts"][0]["data"]["hold_id"]
            if not isinstance(venue_hold, str) or not venue_hold or not room.get("id"):
                raise ValueError("Venue confirmation has no hold identifier")
            return {
                "reserved": True,
                "hotel_hold": hold_id,
                "venue": room["id"],
                "charged_cents": 0,
            }
    except (httpx.HTTPError, KeyError, ValueError, TypeError, IndexError):
        # The venue may have committed before the response was lost. Cancel by
        # idempotency key, creating a tombstone that also fences a late retry.
        try:
            cleanup = await venue.post(
                "/message:send",
                json=as_dict(
                    request({"action": "release_request", "request_id": request_id + ":venue"})
                ),
            )
            cleanup.raise_for_status()
            uncertain_cleanup = cleanup.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
        except (httpx.HTTPError, KeyError, ValueError, TypeError, IndexError):
            uncertain_cleanup = False
    compensated = False
    try:
        released_response = await travel.post(
            "/message:send", json=as_dict(request({"action": "release", "hold_id": hold_id}))
        )
        released_response.raise_for_status()
        released = released_response.json()["task"]
        compensated = released["status"]["state"] == "TASK_STATE_COMPLETED" and uncertain_cleanup
    except (httpx.HTTPError, KeyError, ValueError, TypeError, IndexError):
        pass
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
