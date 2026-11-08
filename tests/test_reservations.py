"""Crash-safe business compensation across independently owned A2A agents."""

import asyncio

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from agents.app import make_handler
from agents.concierge import Concierge
from agents.reservations import ReservationExecutor
from common.reservations import ReservationStore
from common.saga import reserve_pair
from common.testing import client


async def test_idempotency_owner_and_restart(tmp_path):
    url = "sqlite+aiosqlite:///" + (tmp_path / "holds.db").as_posix()
    first = create_async_engine(url)
    store = ReservationStore(first, "travel")
    await store.initialize()
    results = await asyncio.gather(*[store.reserve("maplewood:one", "event-42") for _ in range(5)])
    assert len({r["hold_id"] for r in results}) == 1
    await first.dispose()
    second = create_async_engine(url)
    try:
        store = ReservationStore(second, "travel")
        assert await store.reserve("maplewood:one", "event-42") == results[0]
        with pytest.raises(ValueError, match="not found"):
            await store.release("other:one", results[0]["hold_id"])
        for _ in range(2):
            await store.release("maplewood:one", results[0]["hold_id"])
        with pytest.raises(ValueError, match="released"):
            await store.reserve("maplewood:one", "event-42")
    finally:
        await second.dispose()


async def test_compensate_response_lost_after_venue_commit(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite:///" + (tmp_path / "saga.db").as_posix())
    hotel, venue = ReservationStore(engine, "travel"), ReservationStore(engine, "venues")
    await hotel.initialize()
    await venue.initialize()
    try:
        async with client(
            "travel", handler=make_handler("travel", executor=ReservationExecutor("travel", hotel))
        ) as travel:
            async with client(
                "venues",
                handler=make_handler("venues", executor=ReservationExecutor("venues", venue)),
            ) as venues:

                class LostReply:
                    async def post(self, path, **kwargs):
                        response = await venues.post(path, **kwargs)
                        if kwargs["json"]["message"]["parts"][0]["data"]["action"] == "hold":
                            raise httpx.ReadError("Lost after commit")
                        return response

                result = await reserve_pair(travel, LostReply(), "event-42")
                assert result["compensated"] and not result["manual_followup_required"]
                async with engine.connect() as connection:
                    for store in (hotel, venue):
                        assert (
                            await connection.execute(select(store.holds.c.state))
                        ).scalars().all() == ["released"]
    finally:
        await engine.dispose()


async def test_flagship_plan_runs_holds_and_compensation(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite:///" + (tmp_path / "flagship.db").as_posix())
    try:
        async with client(
            "travel",
            handler=make_handler(
                "travel", executor=ReservationExecutor("travel", ReservationStore(engine, "travel"))
            ),
        ) as travel:
            async with client(
                "venues",
                handler=make_handler(
                    "venues",
                    executor=ReservationExecutor(
                        "venues", ReservationStore(engine, "venues"), available=False
                    ),
                ),
            ) as venues:
                plan = await Concierge({"travel": travel, "venues": venues}).plan(
                    {
                        "guests": 40,
                        "needs": ["venues", "travel"],
                        "tentative_holds": True,
                        "hold_request_id": "event-42",
                        "budget_cents": 1000000,
                    }
                )
                assert plan["approval_required"]
                assert plan["reservations"]["compensated"]
                assert plan["reservations"]["charged_cents"] == 0
    finally:
        await engine.dispose()


async def test_lost_first_hold_reply_is_reconciled(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite:///" + (tmp_path / "first-hold.db").as_posix())
    store = ReservationStore(engine, "travel")
    try:
        async with client(
            "travel", handler=make_handler("travel", executor=ReservationExecutor("travel", store))
        ) as travel:

            class LostReply:
                async def post(self, path, **kwargs):
                    response = await travel.post(path, **kwargs)
                    if kwargs["json"]["message"]["parts"][0]["data"]["action"] == "hold":
                        raise httpx.ReadError("Lost hotel acknowledgement after commit")
                    return response

            result = await reserve_pair(LostReply(), None, "first-hold")
            assert result["compensated"] and not result["manual_followup_required"]
            async with engine.connect() as connection:
                assert (await connection.execute(select(store.holds.c.state))).scalars().all() == [
                    "released"
                ]
    finally:
        await engine.dispose()


async def test_unreachable_cleanup_requires_manual_followup():
    class Unreachable:
        async def post(self, *args, **kwargs):
            raise httpx.ConnectError("Synthetic unreachable partner")

    result = await reserve_pair(Unreachable(), None, "unreachable")
    assert result == {
        "reserved": False,
        "compensated": False,
        "manual_followup_required": True,
        "charged_cents": 0,
    }
