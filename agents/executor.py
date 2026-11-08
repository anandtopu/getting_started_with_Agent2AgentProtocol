"""A task-first executor: paused tasks retain their brief in task metadata."""

import asyncio

from a2a.helpers import (
    new_task_from_user_message,
    new_text_artifact_update_event,
    new_text_status_update_event,
)
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Artifact, TaskArtifactUpdateEvent, TaskState
from google.protobuf.json_format import MessageToDict, ParseDict

from agents.business import quote
from agents.catalog import QUOTE_EXTENSION
from common.artifact_files import quote_pdf
from common.observability import record_task
from common.protocol import brief_from, data_part


class VendorExecutor(AgentExecutor):
    def __init__(self, vendor: str):
        self.vendor = vendor

    async def produce_quote(self, brief, *, partner=False):
        return quote(self.vendor, brief, partner=partner)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        record_task(task, self.vendor, context)
        brief = MessageToDict(task.metadata).get("brief", {})
        brief.update(brief_from(context.message))
        ParseDict({"brief": brief}, task.metadata)
        # KEY IDEA: introduce a new task once. The 1.3 handler owns resumed snapshots.
        if context.current_task is None:
            await event_queue.enqueue_event(task)

        async def state(value: int, text: str) -> None:
            await event_queue.enqueue_event(
                new_text_status_update_event(task.id, task.context_id, value, text)
            )

        await state(TaskState.TASK_STATE_WORKING, f"{self.vendor}: checking the brief")
        if self.vendor == "catering" and "dietary" not in brief:
            await state(
                TaskState.TASK_STATE_INPUT_REQUIRED, "How many guests need each dietary option?"
            )
            return
        if brief.get("require_partner") and not context.call_context.state.get("partner", False):
            await state(
                TaskState.TASK_STATE_AUTH_REQUIRED,
                "Obtain partner authorization outside this conversation.",
            )
            return
        if brief.get("simulate_failure"):
            await state(
                TaskState.TASK_STATE_FAILED, "Synthetic supplier outage; no booking was made."
            )
            return
        if brief.get("wait_for_confirmation"):
            await asyncio.sleep(min(float(brief.get("delay_seconds", 0.05)), 2.0))
        try:
            result = await self.produce_quote(
                brief, partner=context.call_context.state.get("partner", False)
            )
        except TimeoutError:
            await state(
                TaskState.TASK_STATE_FAILED, "Vendor workflow timed out; no booking was made."
            )
            return
        except (ValueError, TypeError) as exc:
            await state(TaskState.TASK_STATE_REJECTED, str(exc))
            return
        if self.vendor == "av":
            for index, text in enumerate(
                ["Microphone check. ", "Projector alignment. ", "Sound check complete."]
            ):
                await event_queue.enqueue_event(
                    new_text_artifact_update_event(
                        task.id,
                        task.context_id,
                        "setup-plan",
                        text,
                        artifact_id="plan",
                        append=index > 0,
                        last_chunk=index == 2,
                    )
                )
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                last_chunk=True,
                artifact=Artifact(
                    artifact_id="quote",
                    name="quote",
                    parts=[data_part(result)]
                    + (
                        [quote_pdf(int(result["guests"]), int(result["total_cents"]))]
                        if self.vendor == "catering" and brief.get("include_files")
                        else []
                    ),
                    extensions=[QUOTE_EXTENSION]
                    if QUOTE_EXTENSION in context.requested_extensions
                    else [],
                ),
            )
        )
        if self.vendor == "venues" and brief.get("include_files"):
            from common.artifact_files import floor_plan

            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    task_id=task.id,
                    context_id=task.context_id,
                    artifact=Artifact(artifact_id="floor-plan", parts=[floor_plan()]),
                    last_chunk=True,
                )
            )
        await state(TaskState.TASK_STATE_COMPLETED, "Quote ready; no money has been spent.")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(
            new_text_status_update_event(
                context.task_id,
                context.context_id,
                TaskState.TASK_STATE_CANCELED,
                "Work canceled. No booking was made.",
            )
        )
