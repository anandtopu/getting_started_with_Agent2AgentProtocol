"""Durable, owner-scoped, idempotent tentative holds; no purchase capability."""

import asyncio
import time
from uuid import uuid4

from sqlalchemy import Column, Float, MetaData, String, Table, insert, select, update
from sqlalchemy.exc import IntegrityError


class ReservationStore:
    def __init__(self, engine, vendor, *, clock=time.time):
        self.engine, self.clock = engine, clock
        self.metadata = MetaData()
        self.holds = Table(
            vendor + "_holds",
            self.metadata,
            Column("owner", String(255), primary_key=True),
            Column("request_id", String(128), primary_key=True),
            Column("id", String(36), unique=True, nullable=False),
            Column("state", String(16), nullable=False),
            Column("expires", Float, nullable=False),
        )
        self.ready, self.lock = False, asyncio.Lock()

    async def initialize(self):
        async with self.lock:
            if not self.ready:
                async with self.engine.begin() as connection:
                    await connection.run_sync(self.metadata.create_all)
                self.ready = True

    async def reserve(self, owner, request_id, *, available=True):
        await self.initialize()
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
            raise ValueError("A bounded idempotency request_id is required")

        async def existing():
            async with self.engine.connect() as connection:
                return (
                    (
                        await connection.execute(
                            select(self.holds).where(
                                self.holds.c.owner == owner, self.holds.c.request_id == request_id
                            )
                        )
                    )
                    .mappings()
                    .first()
                )

        row = await existing()
        if row is None:
            if not available:
                raise ValueError("No tentative hold available")
            try:
                async with self.engine.begin() as connection:
                    await connection.execute(
                        insert(self.holds).values(
                            owner=owner,
                            request_id=request_id,
                            id=str(uuid4()),
                            state="held",
                            expires=self.clock() + 900,
                        )
                    )
            except IntegrityError:
                pass  # A concurrent retry won; read its same durable result.
            row = await existing()
        if row["state"] != "held" or row["expires"] <= self.clock():
            raise ValueError("Hold request already released or expired; use a new request ID")
        return {"hold_id": row["id"], "expires_at": row["expires"], "charged_cents": 0}

    async def release(self, owner, hold_id):
        await self.initialize()
        async with self.engine.begin() as connection:
            result = await connection.execute(
                update(self.holds)
                .where(self.holds.c.owner == owner, self.holds.c.id == hold_id)
                .values(state="released")
            )
        if result.rowcount != 1:
            raise ValueError("Hold not found")
        return {"released": hold_id, "charged_cents": 0}

    async def release_request(self, owner, request_id):
        """Cancel even an uncertain hold; a tombstone fences a late retry."""
        await self.initialize()
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
            raise ValueError("Invalid request_id")
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        statement = pg_insert if self.engine.dialect.name == "postgresql" else sqlite_insert
        async with self.engine.begin() as connection:
            await connection.execute(
                statement(self.holds)
                .values(
                    owner=owner, request_id=request_id, id=str(uuid4()), state="released", expires=0
                )
                .on_conflict_do_update(
                    index_elements=[self.holds.c.owner, self.holds.c.request_id],
                    set_={"state": "released"},
                )
            )
        return {"released_request": request_id, "charged_cents": 0}
