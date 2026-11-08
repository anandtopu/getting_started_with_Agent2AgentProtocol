"""Independent connections exercise real failure boundaries, not mock databases."""

import asyncio
import os
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from a2a.auth.user import User
from a2a.server.cluster.event_stream import VersionedEvent
from a2a.server.cluster.task_store import ConcurrentTaskModificationError
from a2a.server.cluster.version import TaskVersion
from a2a.server.context import ServerCallContext
from a2a.types import (
    ListTasksRequest,
    SubscribeToTaskRequest,
    Task,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from google.protobuf.json_format import ParseDict
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import create_async_engine

from agents.app import make_handler
from common.cluster import ClusterStore
from common.protocol import as_dict, request
from common.testing import client


class TestUser(User):
    __test__ = False

    def __init__(self, name):
        self.name = name

    @property
    def user_name(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


@asynccontextmanager
async def replicas(tmp_path):
    url = (
        os.environ.get("MAPLEWOOD_TEST_DATABASE")
        or "sqlite+aiosqlite:///" + (tmp_path / "cluster.db").as_posix()
    )
    engines = [create_async_engine(url), create_async_engine(url)]
    namespace = "cluster" if "MAPLEWOOD_TEST_DATABASE" not in os.environ else "test_" + uuid4().hex
    stores = [
        ClusterStore(e, namespace, destinations=["https://receiver.test/notifications"])
        for e in engines
    ]
    try:
        for store in stores:
            await store.initialize()
        yield stores
    finally:
        for engine in engines:
            await engine.dispose()


def task(state=TaskState.TASK_STATE_WORKING):
    return Task(id="test-task", context_id="project", status=TaskStatus(state=state))


async def save(store, value=None, version=TaskVersion.MISSING, context=None):
    value = value or task()
    return await store.save(
        value,
        event=TaskStatusUpdateEvent(
            task_id=value.id, context_id=value.context_id, status=value.status
        ),
        prev=None,
        prev_version=version,
        context=context or ServerCallContext(),
    )


async def test_stale_writer_cannot_overwrite_and_cancel_wins(tmp_path):
    async with replicas(tmp_path) as (one, two):
        version = await save(one)
        current = await save(two, version=version)
        with pytest.raises(ConcurrentTaskModificationError):
            await save(one, version=version)
        canceled = await save(one, task(TaskState.TASK_STATE_CANCELED), version)
        assert canceled.is_after(current)
        with pytest.raises(ConcurrentTaskModificationError):
            await save(two, task(TaskState.TASK_STATE_CANCELED), canceled)


async def test_transaction_failure_rolls_back_task_journal_and_outbox(tmp_path):
    async with replicas(tmp_path) as (one, two):

        def fault(conn, cursor, statement, parameters, context, many):
            if statement.startswith("INSERT INTO " + one.outbox.name):
                raise RuntimeError("simulated disk failure")

        event.listen(one.engine.sync_engine, "before_cursor_execute", fault)
        try:
            with pytest.raises(RuntimeError, match="disk failure"):
                await save(one)
        finally:
            event.remove(one.engine.sync_engine, "before_cursor_execute", fault)
        assert await two.get("test-task", ServerCallContext()) is None
        assert not (await two.list(ListTasksRequest(), ServerCallContext())).tasks
        async with two.engine.connect() as connection:
            assert not (await connection.execute(select(two.events))).all()
            assert not (await connection.execute(select(two.outbox))).all()


async def test_crash_before_publish_and_reconnect_on_another_replica(tmp_path):
    async with replicas(tmp_path) as (one, two):
        first = await save(one)
        second = await save(one, version=first)  # publisher dies BEFORE publish()
        stream = two.subscribe("test-task", after=first)
        assert (await asyncio.wait_for(anext(stream), 1)).version == second
        await stream.aclose()  # connection lost
        final = await save(one, task(TaskState.TASK_STATE_COMPLETED), second)
        await one.destroy("test-task")
        stream = two.subscribe("test-task", after=second)
        recovered = await asyncio.wait_for(anext(stream), 1)
        assert recovered.version == final
        assert recovered.event.status.state == TaskState.TASK_STATE_COMPLETED
        await stream.aclose()


async def test_lease_expiration_fences_old_worker_and_dead_letters(tmp_path):
    async with replicas(tmp_path) as (one, two):
        await save(one)
        claim = await one.claim(now=100, seconds=5)
        assert await two.claim(now=101) is None
        recovered = await two.claim(now=106)
        assert recovered["id"] == claim["id"]
        assert not await one.acknowledge(claim, True, now=107)
        assert await two.acknowledge(recovered, False, now=107, max_attempts=2)
        assert await one.claim(now=1000) is None


async def test_distributed_budget_and_window_reset(tmp_path):
    async with replicas(tmp_path) as stores:
        outcomes = await asyncio.gather(
            *[stores[i % 2].allow("tenant:user", now=100, limit=3) for i in range(12)]
        )
        assert sum(outcomes) == 3
        assert await stores[1].allow("another:user", now=100, limit=3)
        assert await stores[0].allow("tenant:user", now=180, limit=3)


async def test_sdk_pause_resume_across_handlers_with_cluster_store(tmp_path):
    async with replicas(tmp_path) as (one, two):
        async with client("catering", handler=make_handler("catering", task_store=one)) as http:
            first = (
                await http.post("/message:send", json=as_dict(request({"guests": 40})))
            ).json()["task"]
        async with client("catering", handler=make_handler("catering", task_store=two)) as http:
            follow = request(
                {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
            )
            response = await http.post("/message:send", json=as_dict(follow))
            assert response.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED"


async def test_owner_cannot_read_delete_or_reuse_another_owners_id(tmp_path):
    async with replicas(tmp_path) as (one, two):
        owner = ServerCallContext(user=TestUser("maplewood:planner"))
        stranger = ServerCallContext(user=TestUser("other:planner"))
        version = await save(one, context=owner)
        assert await two.get("test-task", stranger) is None
        await two.delete("test-task", stranger)
        assert (await one.get("test-task", owner)).version == version
        with pytest.raises(ConcurrentTaskModificationError):
            await save(two, context=stranger)


async def test_semantically_equal_protobuf_publication(tmp_path):
    async with replicas(tmp_path) as (one, two):
        value = task()
        ParseDict({"a": {"z": 1, "x": 2}, "b": [1, 2, 3]}, value.metadata)
        version = await one.save(
            value,
            event=value,
            prev=None,
            prev_version=TaskVersion.MISSING,
            context=ServerCallContext(),
        )
        copied = Task.FromString(value.SerializeToString())
        await two.publish(value.id, VersionedEvent(copied, version))
        copied.metadata["b"] = "tampered"
        with pytest.raises(ValueError, match="atomically"):
            await two.publish(value.id, VersionedEvent(copied, version))


async def test_sdk_reconnect_moves_subscription_to_another_replica(tmp_path):
    async with replicas(tmp_path) as (one, two):
        handlers = [make_handler("av", task_store=s) for s in (one, two)]
        context = ServerCallContext()
        try:
            message = request({"guests": 40, "wait_for_confirmation": True, "delay_seconds": 0.5})
            message.configuration.return_immediately = True
            response = await handlers[0].on_message_send(message, context)
            task_id = response.id
            subscription = handlers[1].on_subscribe_to_task(
                SubscribeToTaskRequest(id=task_id), context
            )
            initial = await asyncio.wait_for(anext(subscription), 2)
            assert isinstance(initial, Task) and initial.id == task_id
            await subscription.aclose()  # client loses its connection
            restarted = handlers[1].on_subscribe_to_task(
                SubscribeToTaskRequest(id=task_id), context
            )
            observed = []
            async with asyncio.timeout(5):
                async for item in restarted:
                    observed.append(item)
            assert isinstance(observed[0], Task)
            assert any(
                isinstance(e, TaskStatusUpdateEvent)
                and e.status.state == TaskState.TASK_STATE_COMPLETED
                for e in observed
            )
            assert (await two.get(task_id, context)).task.artifacts
        finally:
            for handler in handlers:
                await handler.aclose()
