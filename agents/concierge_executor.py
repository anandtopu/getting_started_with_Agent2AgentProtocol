"""Expose the Concierge over A2A using the same task contract as its vendors."""

from contextlib import AsyncExitStack

import httpx
from a2a.helpers import new_task_from_user_message, new_text_status_update_event
from a2a.server.agent_execution import AgentExecutor
from a2a.types import Artifact, TaskArtifactUpdateEvent, TaskState
from google.protobuf.json_format import MessageToDict, ParseDict

from agents.concierge import Concierge
from agents.executor import VendorExecutor
from common.card_trust import verify_vendor
from common.config import url
from common.protocol import brief_from, data_part
from common.remote import GrpcRemote


class ConciergeExecutor(AgentExecutor):
    def __init__(self, tokens: dict[str, str]):
        self.tokens = tokens

    async def execute(self, context, event_queue):
        task = context.current_task or new_task_from_user_message(context.message)
        brief = MessageToDict(task.metadata).get("brief", {})
        brief.update(brief_from(context.message))
        ParseDict({"brief": brief}, task.metadata)
        previous = next(
            (MessageToDict(a.parts[0].data) for a in task.artifacts if a.artifact_id == "plan"),
            None,
        )
        if context.current_task is None:
            await event_queue.enqueue_event(task)
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id, task.context_id, TaskState.TASK_STATE_WORKING, "Collecting vendor quotes"
            )
        )
        async with AsyncExitStack() as stack:
            # Discovery is read from a configured URL; only its pinned vendor key is accepted.
            async with httpx.AsyncClient(timeout=5) as discovery:
                for vendor in self.tokens:
                    response = await discovery.get(url(vendor) + "/.well-known/agent-card.json")
                    response.raise_for_status()
                    verify_vendor(response.json(), vendor)
            clients = {
                vendor: await stack.enter_async_context(
                    GrpcRemote(token)
                    if vendor == "print"
                    else httpx.AsyncClient(
                        base_url=url(vendor),
                        headers={"Authorization": f"Bearer {token}", "A2A-Version": "1.0"},
                    )
                )
                for vendor, token in self.tokens.items()
            }
            result = await Concierge(clients).plan(brief, previous)
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                artifact=Artifact(artifact_id="plan", name="event-plan", parts=[data_part(result)]),
                last_chunk=True,
            )
        )
        states = {d["state"] for d in result["delegations"]}
        state = next(
            (
                TaskState.Value(s)
                for s in (
                    "TASK_STATE_FAILED",
                    "TASK_STATE_REJECTED",
                    "TASK_STATE_AUTH_REQUIRED",
                    "TASK_STATE_INPUT_REQUIRED",
                )
                if s in states
            ),
            TaskState.TASK_STATE_COMPLETED,
        )
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id,
                task.context_id,
                state,
                "Review quotes and missing information before approval.",
            )
        )

    async def cancel(self, context, event_queue):
        await VendorExecutor("venues").cancel(context, event_queue)
