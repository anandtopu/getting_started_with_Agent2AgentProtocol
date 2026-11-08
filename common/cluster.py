"""SQL-backed SDK cluster interfaces and an atomic, leased notification outbox.

SQLite is useful for the offline failure labs; PostgreSQL supports replicas.
Initialize the schema before starting replicas. Events remain until explicit task
deletion so a slow subscriber can read the terminal event after its publisher exits.
"""

import asyncio
import json
import re
import time
from functools import lru_cache
from uuid import uuid4

import httpx
from a2a.server.cluster.event_stream import TaskEventStream, VersionedEvent
from a2a.server.cluster.task_store import (
    ConcurrentTaskModificationError,
    StoredTask,
    VersionedTaskStore,
)
from a2a.server.cluster.version import TaskVersion
from a2a.server.models import create_task_model
from a2a.server.owner_resolver import resolve_user_scope
from a2a.server.tasks import DatabaseTaskStore
from a2a.server.tasks.push_notification_sender import PushNotificationSender
from a2a.types import (
    Message,
    Task,
    TaskArtifactUpdateEvent,
    TaskPushNotificationConfig,
    TaskState,
    TaskStatusUpdateEvent,
)
from google.protobuf.json_format import MessageToDict, Parse
from sqlalchemy import (
    Column,
    Float,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase

TERMINAL = {
    TaskState.TASK_STATE_COMPLETED,
    TaskState.TASK_STATE_FAILED,
    TaskState.TASK_STATE_CANCELED,
    TaskState.TASK_STATE_REJECTED,
}
EVENTS = {t.__name__: t for t in (Task, Message, TaskStatusUpdateEvent, TaskArtifactUpdateEvent)}


@lru_cache
def task_model(namespace):
    class ClusterBase(DeclarativeBase):
        pass

    return create_task_model(namespace + "_tasks", base=ClusterBase)


class ClusterStore(VersionedTaskStore, TaskEventStream):
    def __init__(self, engine, namespace="cluster", *, destinations=(), callbacks=None):
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,23}", namespace):
            raise ValueError("Database namespace must be a lowercase identifier of 1–24 characters")
        self.engine = engine
        self.legacy = DatabaseTaskStore(engine, create_table=False)
        self.legacy.task_model = task_model(namespace)
        self.destinations = tuple(destinations)
        self.callbacks = callbacks
        self.metadata = MetaData()
        self.revisions = Table(
            namespace + "_revisions",
            self.metadata,
            Column("id", String(36), primary_key=True),
            Column("owner", String(255), nullable=False),
            Column("version", Integer, nullable=False),
            Column("state", Integer, nullable=False),
            Column("snapshot", LargeBinary, nullable=False),
        )
        self.events = Table(
            namespace + "_events",
            self.metadata,
            Column("id", String(36), primary_key=True),
            Column("version", Integer, primary_key=True),
            Column("kind", String(64), nullable=False),
            Column("body", LargeBinary, nullable=False),
        )
        self.outbox = Table(
            namespace + "_outbox",
            self.metadata,
            Column("id", String(36), primary_key=True),
            Column("task_id", String(36), nullable=False),
            Column("url", String(2048), nullable=False),
            Column("body", LargeBinary, nullable=False),
            Column("attempts", Integer, nullable=False, default=0),
            Column("due", Float, nullable=False, default=0),
            Column("lease", String(36)),
            Column("lease_until", Float, nullable=False, default=0),
            Column("state", String(16), nullable=False, default="pending"),
        )
        self.budgets = Table(
            namespace + "_budgets",
            self.metadata,
            Column("subject", String(255), primary_key=True),
            Column("window", Integer, nullable=False),
            Column("count", Integer, nullable=False),
        )
        self._ready = False
        self._init_lock = asyncio.Lock()

    async def initialize(self):
        async with self._init_lock:
            if not self._ready:
                await self.legacy.initialize()
                if self.callbacks:
                    await self.callbacks.initialize()
                async with self.engine.begin() as connection:
                    if self.engine.dialect.name == "sqlite":
                        await connection.exec_driver_sql("PRAGMA journal_mode=WAL")
                    await connection.run_sync(self.legacy.task_model.metadata.create_all)
                    await connection.run_sync(self.metadata.create_all)
                self._ready = True

    async def save(self, task, *, event, prev, prev_version, context):
        await self.initialize()
        owner = resolve_user_scope(context)
        try:
            async with self.legacy.async_session_maker.begin() as session:
                row = (
                    (
                        await session.execute(
                            select(self.revisions).where(self.revisions.c.id == task.id)
                        )
                    )
                    .mappings()
                    .first()
                )
                cancel = task.status.state == TaskState.TASK_STATE_CANCELED
                if row:
                    if row["owner"] != owner or (cancel and row["state"] in TERMINAL):
                        raise ConcurrentTaskModificationError(task.id)
                    if not cancel and TaskVersion(row["version"]) != prev_version:
                        raise ConcurrentTaskModificationError(task.id)
                    # The CAS is in SQL: two independently connected processes cannot win.
                    changed = await session.execute(
                        update(self.revisions)
                        .where(
                            self.revisions.c.id == task.id,
                            self.revisions.c.owner == owner,
                            self.revisions.c.state.not_in(TERMINAL)
                            if cancel
                            else self.revisions.c.version == row["version"],
                        )
                        .values(
                            version=self.revisions.c.version + 1,
                            state=task.status.state,
                            snapshot=task.SerializeToString(),
                        )
                        .returning(self.revisions.c.version)
                    )
                    version = changed.scalar_one_or_none()
                    if version is None:
                        raise ConcurrentTaskModificationError(task.id)
                else:
                    if cancel or not prev_version.is_missing:
                        raise ConcurrentTaskModificationError(task.id)
                    version = 1
                    await session.execute(
                        insert(self.revisions).values(
                            id=task.id,
                            owner=owner,
                            version=version,
                            state=task.status.state,
                            snapshot=task.SerializeToString(),
                        )
                    )
                # Public SDK model/table and conversion hooks are pinned by contract tests.
                model = self.legacy.task_model(
                    id=task.id,
                    context_id=task.context_id,
                    kind="task",
                    owner=owner,
                    last_updated=task.status.timestamp.ToDatetime()
                    if task.status.HasField("timestamp")
                    else None,
                    status=MessageToDict(task.status),
                    artifacts=[MessageToDict(a) for a in task.artifacts],
                    history=[MessageToDict(m) for m in task.history],
                    task_metadata=MessageToDict(task.metadata),
                    protocol_version="1.0",
                )
                await session.merge(model)
                if event is not None:
                    await session.execute(
                        insert(self.events).values(
                            id=task.id,
                            version=version,
                            kind=type(event).__name__,
                            body=event.SerializeToString(),
                        )
                    )
                    field = {
                        Task: "task",
                        Message: "message",
                        TaskStatusUpdateEvent: "statusUpdate",
                        TaskArtifactUpdateEvent: "artifactUpdate",
                    }[type(event)]
                    body = json.dumps({field: MessageToDict(event)}).encode()
                    urls = set(self.destinations)
                    if self.callbacks:
                        configs = (
                            await session.execute(
                                select(self.callbacks.config_model).where(
                                    self.callbacks.config_model.task_id == task.id,
                                    self.callbacks.config_model.owner == owner,
                                )
                            )
                        ).scalars()
                        for config in configs:
                            # This store is deliberately credential-free. HMAC secrets live
                            # only in dispatcher configuration, never in callback records.
                            urls.add(Parse(config.config_data, TaskPushNotificationConfig()).url)
                    for url in urls:
                        await session.execute(
                            insert(self.outbox).values(
                                id=str(uuid4()), task_id=task.id, url=url, body=body
                            )
                        )
                # Flush is inside the transaction: failure rolls back ALL four writes.
                await session.flush()
        except IntegrityError as exc:
            raise ConcurrentTaskModificationError(task.id) from exc
        return TaskVersion(version)

    async def get(self, task_id, context):
        await self.initialize()
        async with self.engine.connect() as connection:
            row = (
                (
                    await connection.execute(
                        select(self.revisions).where(
                            self.revisions.c.id == task_id,
                            self.revisions.c.owner == resolve_user_scope(context),
                        )
                    )
                )
                .mappings()
                .first()
            )
        return (
            StoredTask(Task.FromString(row["snapshot"]), TaskVersion(row["version"]))
            if row
            else None
        )

    async def list(self, params, context):
        await self.initialize()
        return await self.legacy.list(params, context)

    async def delete(self, task_id, context):
        await self.initialize()
        async with self.engine.begin() as connection:
            removed = await connection.execute(
                delete(self.revisions).where(
                    self.revisions.c.id == task_id,
                    self.revisions.c.owner == resolve_user_scope(context),
                )
            )
            if removed.rowcount:
                await connection.execute(delete(self.events).where(self.events.c.id == task_id))
                await connection.execute(
                    delete(self.outbox).where(self.outbox.c.task_id == task_id)
                )
                await connection.execute(
                    delete(self.legacy.task_model).where(self.legacy.task_model.id == task_id)
                )

    async def publish(self, task_id, event):
        # save() already committed the event. This verifies integration mistakes instead
        # of creating a second non-atomic publication path or duplicating delivery.
        async with self.engine.connect() as connection:
            rows = (
                (await connection.execute(select(self.events).where(self.events.c.id == task_id)))
                .mappings()
                .all()
            )
            if not any(
                TaskVersion(r["version"]) == event.version
                and EVENTS[r["kind"]].FromString(r["body"]) == event.event
                for r in rows
            ):
                raise ValueError("Publish requires an atomically committed event")

    async def subscribe(self, task_id, *, after):
        await self.initialize()
        cursor = after
        while True:
            async with self.engine.connect() as connection:
                rows = (
                    (
                        await connection.execute(
                            select(self.events)
                            .where(self.events.c.id == task_id)
                            .order_by(self.events.c.version)
                        )
                    )
                    .mappings()
                    .all()
                )
            for row in rows:
                version = TaskVersion(row["version"])
                if version.is_after(cursor):
                    cursor = version
                    yield VersionedEvent(EVENTS[row["kind"]].FromString(row["body"]), version)
            await asyncio.sleep(0.02)

    async def destroy(self, task_id):
        # No live broker resources. Explicit owner-authorized delete applies retention.
        return None

    async def claim(self, *, now=None, seconds=30):
        """Lease one eligible delivery; expired claims may be recovered after a crash."""
        await self.initialize()
        now = time.time() if now is None else now
        eligible = (
            self.outbox.c.state == "pending",
            self.outbox.c.due <= now,
            self.outbox.c.lease_until <= now,
        )
        async with self.engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        select(self.outbox)
                        .where(*eligible)
                        .order_by(self.outbox.c.due, self.outbox.c.id)
                        .limit(1)
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            lease = str(uuid4())
            result = await connection.execute(
                update(self.outbox)
                .where(self.outbox.c.id == row["id"], *eligible)
                .values(lease=lease, lease_until=now + seconds, attempts=row["attempts"] + 1)
            )
            return dict(row, lease=lease, attempts=row["attempts"] + 1) if result.rowcount else None

    async def acknowledge(self, claim, success, *, now=None, max_attempts=8):
        now = time.time() if now is None else now
        state = (
            "delivered" if success else "dead" if claim["attempts"] >= max_attempts else "pending"
        )
        async with self.engine.begin() as connection:
            result = await connection.execute(
                update(self.outbox)
                .where(
                    self.outbox.c.id == claim["id"],
                    self.outbox.c.lease == claim["lease"],
                    self.outbox.c.lease_until > now,
                    self.outbox.c.state == "pending",
                )
                .values(
                    state=state,
                    lease=None,
                    lease_until=0,
                    due=now + min(300, 2 ** min(claim["attempts"], 8)),
                )
            )
        return result.rowcount == 1

    async def dispatch(self, client, destinations, *, limit=100):
        """Bounded at-least-once delivery; callers schedule another pass after backoff."""
        from common.security import webhook_headers

        delivered = 0
        for _ in range(limit):
            claim = await self.claim()
            if claim is None:
                break
            success = False
            if claim["url"] in destinations:
                headers = webhook_headers(claim["body"], destinations[claim["url"]], claim["id"])
                headers["Content-Type"] = "application/a2a+json"
                try:
                    response = await client.post(
                        claim["url"],
                        content=claim["body"],
                        headers=headers,
                        timeout=3,
                        follow_redirects=False,
                    )
                    success = 200 <= response.status_code < 300
                except httpx.TransportError:
                    pass
            acknowledged = await self.acknowledge(claim, success)
            delivered += int(success and acknowledged)
        return delivered

    async def allow(self, subject, *, now=None, limit=120, window_seconds=60):
        """Atomic fixed-window budget shared by all workers; identity is authenticated."""
        await self.initialize()
        now = time.time() if now is None else now
        window = int(now // window_seconds)
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        statement = pg_insert if self.engine.dialect.name == "postgresql" else sqlite_insert
        async with self.engine.begin() as connection:
            await connection.execute(
                statement(self.budgets)
                .values(subject=subject, window=window, count=0)
                .on_conflict_do_nothing()
            )
            await connection.execute(
                update(self.budgets)
                .where(
                    self.budgets.c.subject == subject,
                    self.budgets.c.window < window,
                )
                .values(window=window, count=0)
            )
            result = await connection.execute(
                update(self.budgets)
                .where(
                    self.budgets.c.subject == subject,
                    self.budgets.c.window == window,
                    self.budgets.c.count < limit,
                )
                .values(count=self.budgets.c.count + 1)
            )
        return result.rowcount == 1


class OutboxSender(PushNotificationSender):
    """SDK wake-up hook. Recovery workers call store.dispatch independently after restart."""

    def __init__(self, store, client, destinations):
        self.store, self.client, self.destinations = store, client, destinations

    async def send_notification(self, task_id, event):
        await self.store.dispatch(self.client, self.destinations)
