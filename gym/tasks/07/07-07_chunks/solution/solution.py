from a2a.helpers import (
    new_task_from_user_message,
    new_text_artifact_update_event,
    new_text_status_update_event,
)
from a2a.server.agent_execution import AgentExecutor
from a2a.types import TaskState


class SetupPlan(AgentExecutor):
    async def execute(self, context, event_queue):
        task = new_task_from_user_message(context.message)
        await event_queue.enqueue_event(task)
        for index, text in enumerate(["Microphones. ", "Projector."]):
            await event_queue.enqueue_event(
                new_text_artifact_update_event(
                    task.id,
                    task.context_id,
                    "plan",
                    text,
                    artifact_id="setup",
                    append=index > 0,
                    last_chunk=index == 1,
                )
            )
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id, task.context_id, TaskState.TASK_STATE_COMPLETED, "Ready."
            )
        )

    async def cancel(self, context, event_queue):
        await event_queue.enqueue_event(
            new_text_status_update_event(
                context.task_id, context.context_id, TaskState.TASK_STATE_CANCELED, "Canceled."
            )
        )


def build():
    # YOUR CODE HERE: repair the chunk boundary above.
    return SetupPlan()
