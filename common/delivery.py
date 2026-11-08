"""Restart-safe notification outbox and inbox; delivery is at least once.

One dispatcher owns an outbox. A transactional inbox deduplicates its signed
delivery IDs. This lab does not claim an atomic transaction with SDK task storage.
"""

import hashlib
import json
import sqlite3
import time
from uuid import uuid4

import httpx
from a2a.types import StreamResponse
from fastapi import FastAPI, Request
from google.protobuf.json_format import ParseDict, ParseError
from starlette.responses import JSONResponse

from common.security import verify_webhook, webhook_headers


class DeliveryStore:
    def __init__(self, path):
        self.database = sqlite3.connect(path)
        self.database.executescript("""
            CREATE TABLE IF NOT EXISTS outbox(
                id TEXT PRIMARY KEY, url TEXT NOT NULL, body BLOB NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, due REAL NOT NULL DEFAULT 0,
                delivered INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS inbox(
                id TEXT PRIMARY KEY, digest TEXT NOT NULL, body BLOB NOT NULL);
        """)

    def close(self):
        self.database.close()

    def enqueue(self, url: str, event: dict) -> str:
        identifier = str(uuid4())
        with self.database:
            self.database.execute(
                "INSERT INTO outbox(id,url,body) VALUES(?,?,?)",
                (identifier, url, json.dumps(event).encode()),
            )
        return identifier

    def accept(self, identifier: str, body: bytes) -> bool:
        digest = hashlib.sha256(body).hexdigest()
        with self.database:
            cursor = self.database.execute(
                "INSERT OR IGNORE INTO inbox VALUES(?,?,?)", (identifier, digest, body)
            )
            existing = self.database.execute(
                "SELECT digest FROM inbox WHERE id=?", (identifier,)
            ).fetchone()
            if existing[0] != digest:
                raise ValueError("Delivery ID reused for a different payload")
            return cursor.rowcount == 1

    def accepted_count(self) -> int:
        return self.database.execute("SELECT COUNT(*) FROM inbox").fetchone()[0]

    def deliveries(self, limit=50):
        return [
            json.loads(row[0])
            for row in self.database.execute(
                "SELECT body FROM inbox ORDER BY rowid DESC LIMIT ?", (limit,)
            ).fetchall()
        ]

    async def dispatch(
        self, client: httpx.AsyncClient, destinations: dict[str, bytes], *, now: float | None = None
    ) -> int:
        now = time.time() if now is None else now
        rows = self.database.execute(
            "SELECT id,url,body,attempts FROM outbox WHERE delivered=0 AND due<=? LIMIT 100", (now,)
        ).fetchall()
        delivered = 0
        for identifier, url, body, attempts in rows:
            if url not in destinations:
                raise ValueError("Outbox destination is not trusted")
            headers = webhook_headers(body, destinations[url], identifier)
            headers["Content-Type"] = "application/a2a+json"
            try:
                response = await client.post(
                    url, content=body, headers=headers, follow_redirects=False, timeout=3
                )
                success = 200 <= response.status_code < 300
            except httpx.TransportError:
                success = False
            with self.database:
                self.database.execute(
                    "UPDATE outbox SET attempts=?,due=?,delivered=? WHERE id=?",
                    (attempts + 1, now + min(300, 2 ** min(attempts, 8)), int(success), identifier),
                )
            delivered += int(success)
        return delivered


def durable_receiver(secret: bytes, store: DeliveryStore):
    app = FastAPI()
    app.state.store = store
    app.state.deliveries = store.deliveries()

    @app.post("/notifications")
    async def notification(request: Request):
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 1_000_000:
                return JSONResponse({"error": "Too large"}, 413)
        try:
            # Authenticate every retry before consulting the durable inbox.
            verify_webhook(bytes(body), dict(request.headers), secret, {})
            event = ParseDict(json.loads(body), StreamResponse())
            if event.WhichOneof("payload") is None:
                raise ValueError("Empty notification")
            fresh = store.accept(request.headers["x-maplewood-nonce"], bytes(body))
        except (ValueError, TypeError, KeyError, ParseError):
            return JSONResponse({"error": "Unverified notification"}, 401)
        if fresh:
            app.state.deliveries.append(json.loads(body))
        return {"accepted": True, "duplicate": not fresh}

    return app
