"""Add durable hold/release skills around any vendor business runtime."""

from a2a.helpers import new_task_from_user_message, new_text_status_update_event
from a2a.types import Artifact, TaskArtifactUpdateEvent, TaskState

from agents.executor import VendorExecutor
from common.protocol import brief_from, data_part


class ReservationExecutor(VendorExecutor):
    def __init__(self, vendor, store, delegate=None, *, available=True):
        super().__init__(vendor)
        self.store, self.delegate, self.available = (
            store,
            delegate or VendorExecutor(vendor),
            available,
        )

    async def execute(self, context, event_queue):
        brief = brief_from(context.message)
        if brief.get("action") not in {"hold", "release", "release_request"}:
            return await self.delegate.execute(context, event_queue)
        task = new_task_from_user_message(context.message)
        await event_queue.enqueue_event(task)
        owner = context.call_context.user.user_name
        try:
            if brief["action"] == "hold":
                result = await self.store.reserve(
                    owner, brief.get("request_id"), available=self.available
                )
            elif brief["action"] == "release_request":
                result = await self.store.release_request(owner, brief.get("request_id"))
            else:
                result = await self.store.release(owner, brief.get("hold_id"))
            state = TaskState.TASK_STATE_COMPLETED
        except ValueError as exc:
            result, state = {"error": str(exc)}, TaskState.TASK_STATE_REJECTED
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                artifact=Artifact(artifact_id="reservation", parts=[data_part(result)]),
                last_chunk=True,
            )
        )
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id,
                task.context_id,
                state,
                "Tentative reservation operation finished; no charge.",
            )
        )
