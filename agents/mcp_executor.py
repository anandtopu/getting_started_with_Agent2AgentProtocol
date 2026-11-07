"""An A2A executor invokes MCP privately; the Concierge sees only A2A artifacts."""

from a2a.helpers import new_task_from_user_message, new_text_status_update_event
from a2a.types import TaskState

from agents.executor import VendorExecutor
from agents.kitchen import check_kitchen
from common.protocol import brief_from


class KitchenExecutor(VendorExecutor):
    def __init__(self):
        super().__init__("catering")

    async def execute(self, context, event_queue):
        brief = brief_from(context.message)
        try:
            await check_kitchen(int(brief.get("guests", 40)))
        except (TypeError, ValueError):
            task = context.current_task or new_task_from_user_message(context.message)
            if context.current_task is None:
                await event_queue.enqueue_event(task)
            await event_queue.enqueue_event(
                new_text_status_update_event(
                    task.id,
                    task.context_id,
                    TaskState.TASK_STATE_REJECTED,
                    "Kitchen capacity is insufficient or the guest count is invalid.",
                )
            )
            return
        await super().execute(context, event_queue)
