"""Tentative, no-charge reservations with an explicit idempotent release skill."""

from uuid import uuid4

from a2a.helpers import new_task_from_user_message, new_text_status_update_event
from a2a.types import Artifact, TaskArtifactUpdateEvent, TaskState

from agents.executor import VendorExecutor
from common.protocol import brief_from, data_part


class HoldExecutor(VendorExecutor):
    def __init__(self, vendor: str, available: bool = True):
        super().__init__(vendor)
        self.available = available
        self.holds = {}
        self.released = {}

    async def execute(self, context, event_queue):
        task = new_task_from_user_message(context.message)
        await event_queue.enqueue_event(task)
        brief = brief_from(context.message)
        owner = context.call_context.user.user_name
        action = brief.get("action")
        if action == "release":
            hold_id = brief.get("hold_id")
            if self.holds.get(hold_id, self.released.get(hold_id)) != owner:
                state, result = TaskState.TASK_STATE_REJECTED, {"error": "Hold not found"}
            else:
                self.holds.pop(hold_id, None)
                self.released[hold_id] = owner
                state, result = TaskState.TASK_STATE_COMPLETED, {"released": hold_id}
        elif action == "hold" and self.available:
            hold_id = str(uuid4())
            self.holds[hold_id] = owner
            state, result = TaskState.TASK_STATE_COMPLETED, {"hold_id": hold_id, "charged_cents": 0}
        else:
            state, result = TaskState.TASK_STATE_REJECTED, {"error": "No tentative hold available"}
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                last_chunk=True,
                artifact=Artifact(artifact_id="reservation", parts=[data_part(result)]),
            )
        )
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id, task.context_id, state, "Tentative reservation operation finished."
            )
        )
