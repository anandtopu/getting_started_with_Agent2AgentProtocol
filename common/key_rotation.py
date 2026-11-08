"""Automated card-key rotation with overlap and an HTTPS-pinned JWKS endpoint."""

import base64
import hashlib
import json
import time
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from starlette.responses import JSONResponse
from starlette.routing import Route

from common.card_trust import jwks
from common.protocol import as_dict
from common.security import sign_card


class SharedCardKeys:
    """Encrypted key ring shared by replicas; optimistic SQL updates fence rotation races.

    The wrapping key is operator configuration outside the database. Changing it
    requires an explicit migration, not silently discarding the established keys.
    """

    def __init__(self, identity, engine, namespace, wrapping_key, *, clock=time.time):
        from cryptography.fernet import Fernet
        from sqlalchemy import Column, Integer, LargeBinary, MetaData, Table

        self.identity, self.engine, self.clock = identity, engine, clock
        self.cipher = Fernet(
            base64.urlsafe_b64encode(
                hashlib.sha256(b"maplewood-card-key-wrap:" + wrapping_key).digest()
            )
        )
        self.metadata = MetaData()
        self.table = Table(
            namespace + "_card_keys",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("revision", Integer, nullable=False),
            Column("body", LargeBinary, nullable=False),
        )
        self.ready = False

    async def initialize(self):
        if not self.ready:
            async with self.engine.begin() as connection:
                await connection.run_sync(self.metadata.create_all)
            self.ready = True

    async def ring(self, revoke=None):
        from sqlalchemy import select, update
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        from common.security import b64, unb64

        await self.initialize()
        statement = pg_insert if self.engine.dialect.name == "postgresql" else sqlite_insert
        for _ in range(10):
            async with self.engine.begin() as connection:
                row = (
                    (await connection.execute(select(self.table).where(self.table.c.id == 1)))
                    .mappings()
                    .first()
                )
                ring = RotatingCardKeys(self.identity, clock=self.clock)
                if row:
                    state = json.loads(self.cipher.decrypt(row["body"]))
                    ring.current, ring.next_rotation = state["current"], state["next_rotation"]
                    ring.keys = {
                        kid: (Ed25519PrivateKey.from_private_bytes(unb64(pair[0])), pair[1])
                        for kid, pair in state["keys"].items()
                    }
                if revoke:
                    ring.revoke(revoke)
                ring.rotate()
                body = self.cipher.encrypt(
                    json.dumps(
                        {
                            "current": ring.current,
                            "next_rotation": ring.next_rotation,
                            "keys": {
                                kid: [b64(key.private_bytes_raw()), expiry]
                                for kid, (key, expiry) in ring.keys.items()
                            },
                        }
                    ).encode()
                )
                if row:
                    result = await connection.execute(
                        update(self.table)
                        .where(self.table.c.id == 1, self.table.c.revision == row["revision"])
                        .values(revision=row["revision"] + 1, body=body)
                    )
                else:
                    result = await connection.execute(
                        statement(self.table)
                        .values(id=1, revision=1, body=body)
                        .on_conflict_do_nothing()
                    )
                if result.rowcount:
                    return ring
        raise RuntimeError("Card rotation contention exceeded retry budget")

    def routes(self):
        async def card(request):
            return JSONResponse((await self.ring()).card())

        async def keys(request):
            return JSONResponse((await self.ring()).public_keys())

        return [Route("/.well-known/agent-card.json", card), Route("/.well-known/jwks.json", keys)]


class RotatingCardKeys:
    def __init__(self, identity, *, interval=300, overlap=90, clock=time.monotonic):
        if interval < 1 or overlap < 30:
            raise ValueError("Rotation interval must be positive; overlap must cover card caching")
        self.identity, self.interval, self.overlap, self.clock = identity, interval, overlap, clock
        self.keys, self.current, self.next_rotation = {}, None, float("-inf")

    def rotate(self):
        now = self.clock()
        if now >= self.next_rotation:
            if self.current in self.keys:
                key, _ = self.keys[self.current]
                self.keys[self.current] = (key, now + self.overlap)
            self.current = "maplewood-" + uuid4().hex
            self.keys[self.current] = (Ed25519PrivateKey.generate(), float("inf"))
            self.next_rotation = now + self.interval
        self.keys = {kid: pair for kid, pair in self.keys.items() if pair[1] > now}

    def card(self):
        self.rotate()
        return sign_card(as_dict(self.identity), self.keys[self.current][0], self.current)

    def public_keys(self):
        self.rotate()
        return {
            "keys": [jwks(key.public_key(), kid)["keys"][0] for kid, (key, _) in self.keys.items()]
        }

    def revoke(self, kid):
        self.keys.pop(kid, None)
        if kid == self.current:
            self.next_rotation = float("-inf")

    def routes(self):
        async def card(request):
            return JSONResponse(self.card())

        async def keys(request):
            return JSONResponse(self.public_keys())

        return [Route("/.well-known/agent-card.json", card), Route("/.well-known/jwks.json", keys)]
