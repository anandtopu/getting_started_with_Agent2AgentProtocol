"""The adapter maps framework results to A2A task events without importing that framework."""

from a2a.helpers import new_task_from_user_message, new_text_status_update_event
from a2a.types import Artifact, TaskArtifactUpdateEvent, TaskState
from google.protobuf.json_format import MessageToDict, ParseDict

from agents.executor import VendorExecutor
from common.frameworks import framework_quote
from common.protocol import brief_from, data_part


class FrameworkVendor(VendorExecutor):
    def __init__(self, vendor: str, framework: str):
        super().__init__(vendor)
        self.framework = framework

    async def execute(self, context, event_queue):
        task = context.current_task or new_task_from_user_message(context.message)
        brief = MessageToDict(task.metadata).get("brief", {})
        brief.update(brief_from(context.message))
        ParseDict({"brief": brief}, task.metadata)
        if context.current_task is None:
            await event_queue.enqueue_event(task)
        if self.vendor == "catering" and "dietary" not in brief:
            await event_queue.enqueue_event(
                new_text_status_update_event(
                    task.id,
                    task.context_id,
                    TaskState.TASK_STATE_INPUT_REQUIRED,
                    "Provide dietary counts.",
                )
            )
            return
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id,
                task.context_id,
                TaskState.TASK_STATE_WORKING,
                "Running the isolated vendor workflow.",
            )
        )
        try:
            result = await framework_quote(self.framework, self.vendor, brief)
            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    task_id=task.id,
                    context_id=task.context_id,
                    last_chunk=True,
                    artifact=Artifact(artifact_id="quote", parts=[data_part(result)]),
                )
            )
            state, text = TaskState.TASK_STATE_COMPLETED, "Quote ready; approval is required."
        except (ValueError, TimeoutError):
            state, text = TaskState.TASK_STATE_FAILED, "Framework worker could not complete safely."
        await event_queue.enqueue_event(
            new_text_status_update_event(task.id, task.context_id, state, text)
        )
