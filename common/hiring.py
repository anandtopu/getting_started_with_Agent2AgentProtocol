"""Synthetic hiring coordination with consent, minimal disclosure and human review."""

from contextlib import AsyncExitStack

from a2a.helpers import new_task_from_user_message, new_text_status_update_event
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import Artifact, TaskArtifactUpdateEvent, TaskState
from google.protobuf.json_format import MessageToDict, ParseDict

from agents.catalog import card
from agents.executor import VendorExecutor
from common.protocol import as_dict, brief_from, data_part, request
from common.testing import client

SLOTS = ["2027-06-01T15:00:00Z", "2027-06-02T16:00:00Z"]


class HiringExecutor(VendorExecutor):
    def __init__(self, role: str, clients=None):
        super().__init__("venues")
        self.role, self.clients = role, clients or {}

    async def execute(self, context, event_queue):
        task = context.current_task or new_task_from_user_message(context.message)
        brief = MessageToDict(task.metadata).get("brief", {})
        brief.update(brief_from(context.message))
        prior = MessageToDict(task.metadata).get("remote", {})
        ParseDict({"brief": brief, "remote": prior}, task.metadata)
        if context.current_task is None:
            await event_queue.enqueue_event(task)
        state = TaskState.TASK_STATE_COMPLETED
        if self.role == "candidate":
            matches = [slot for slot in SLOTS if slot in brief.get("slots", [])]
            if matches:
                result = {"slot": matches[0], "candidate_id": "synthetic-candidate"}
            else:
                state, result = (
                    TaskState.TASK_STATE_INPUT_REQUIRED,
                    {"question": "Propose another UTC time."},
                )
        elif self.role == "background":
            if brief.get("consent") is not True:
                state, result = (
                    TaskState.TASK_STATE_INPUT_REQUIRED,
                    {"question": "Explicit consent is required."},
                )
            else:
                result = {
                    "fixture": True,
                    "status": "synthetic-check-complete",
                    "decision": "human-review-required",
                }
        else:
            delegated = {}
            payloads = {
                "candidate": {"slots": brief.get("slots", [])},
                "background": {"consent": brief.get("consent", False)},
            }
            for role, payload in payloads.items():
                old = prior.get(role)
                if old and old["status"]["state"] == "TASK_STATE_COMPLETED":
                    remote = old
                else:
                    message = request(
                        payload,
                        task_id=old["id"] if old else "",
                        context_id=old["contextId"] if old else "",
                    )
                    response = await self.clients[role].post("/message:send", json=as_dict(message))
                    response.raise_for_status()
                    remote = response.json()["task"]
                delegated[role] = remote
                if remote["status"]["state"] != "TASK_STATE_COMPLETED":
                    state = TaskState.TASK_STATE_INPUT_REQUIRED
            ParseDict({"brief": brief, "remote": delegated}, task.metadata)
            result = {
                "delegations": delegated,
                "hiring_decision": "human-review-required",
                "synthetic_data_only": True,
            }
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                last_chunk=True,
                artifact=Artifact(artifact_id="result", parts=[data_part(result)]),
            )
        )
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id, task.context_id, state, result.get("question", "Review synthetic results.")
            )
        )


def handler(role: str, clients=None):
    identity = card("venues")
    identity.name = "Synthetic hiring: " + role
    identity.skills[0].id = role + ".coordinate"
    identity.skills[
        0
    ].description = "Coordinate synthetic interview logistics with consent; no hiring decision."
    result = DefaultRequestHandler(HiringExecutor(role, clients), InMemoryTaskStore(), identity)
    result.course_card = identity
    return result


async def hiring_lab(records=None):
    records = records if records is not None else []
    async with AsyncExitStack() as stack:
        delegates = {
            role: await stack.enter_async_context(
                client("venues", handler=handler(role), records=records)
            )
            for role in ("candidate", "background")
        }
        recruiter = await stack.enter_async_context(
            client("venues", handler=handler("recruiter", delegates), records=records)
        )
        first = (
            await recruiter.post("/message:send", json=as_dict(request({"slots": [SLOTS[0]]})))
        ).json()["task"]
        followup = request({"consent": True}, task_id=first["id"], context_id=first["contextId"])
        second = (await recruiter.post("/message:send", json=as_dict(followup))).json()["task"]
        return {"before": first, "after": second}
