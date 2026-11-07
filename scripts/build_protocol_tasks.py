"""Author the additional full-boundary gym exercises; generated files are committed."""

import json

from common.config import ROOT

TASKS = [
    (
        "05",
        "07",
        "resume",
        "fix",
        "Resume Saffron without losing its work order",
        "Saffron has asked for dietary counts. Send forty vegan meals on the same task and context.",
        'from common.protocol import as_dict, request\n\nasync def resume(http, first):\n    # YOUR CODE HERE: connect this follow-up to the paused task.\n    message = request({"dietary": {"vegan": 40}})\n    return (await http.post("/message:send", json=as_dict(message))).json()["task"]\n',
        'from common.protocol import as_dict, request\n\nasync def resume(http, first):\n    message = request({"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"])\n    return (await http.post("/message:send", json=as_dict(message))).json()["task"]\n',
        [
            "A project folder is not the same as a work order.",
            "Keep both IDs from the first response.",
            "Pass task_id and context_id to request().",
        ],
    ),
    (
        "08",
        "07",
        "binding",
        "interop",
        "Connect the Concierge to a gRPC-only printer",
        "Send the supplied event brief through the in-process official gRPC service. Return its protobuf response.",
        'from common.protocol import request\n\nasync def quote(service, brief):\n    # YOUR CODE HERE: route to the requested operation with the supplied brief.\n    return await service.unary("SendMessage", request({"guests": 1}))\n',
        'from common.protocol import request\n\nasync def quote(service, brief):\n    return await service.unary("SendMessage", request(brief))\n',
        [
            "The server speaks protobuf, not an HTTP JSON dictionary.",
            "The same operation name exists across bindings.",
            "Call unary with SendMessage and request(brief).",
        ],
    ),
    (
        "13",
        "07",
        "auth",
        "secure",
        "Close Granite's anonymous quote endpoint",
        "Build a server from the supplied token-to-principal map. Reject anonymous calls and isolate task owners.",
        'from agents.app import make_app\n\ndef build(tokens):\n    # YOUR CODE HERE: this accidentally exposes the demo.\n    return make_app("venues", demo=True)\n',
        'from agents.app import make_app\n\ndef build(tokens):\n    return make_app("venues", tokens=tokens)\n',
        [
            "Discovery can be public while work requires authentication.",
            "Use the provided credential map; do not invent a shared identity.",
            "Pass tokens to make_app and leave demo disabled.",
        ],
    ),
    (
        "14",
        "07",
        "signature",
        "secure",
        "Reject a forged skill description",
        "Accept only a card whose signature verifies under the supplied pinned keys. Return a boolean.",
        'def accept(card, keys):\n    # YOUR CODE HERE: the presence of a signature is not proof.\n    return bool(card.get("signatures"))\n',
        "from common.security import verify_card\n\ndef accept(card, keys):\n    try:\n        verify_card(card, keys)\n        return True\n    except ValueError:\n        return False\n",
        [
            "Tampering must invalidate the signature.",
            "Never trust a key supplied by the card itself.",
            "Use verify_card with the pinned map and reject ValueError.",
        ],
    ),
    (
        "15",
        "07",
        "ssrf",
        "secure",
        "Stop artwork URLs reaching internal services",
        "Fetch approved public artwork, but block private and metadata-service destinations before an HTTP call.",
        "async def fetch(url, allowed, client):\n    # YOUR CODE HERE: allow-list membership alone is not enough.\n    response = await client.get(url)\n    return response.content\n",
        "from common.security import fetch_file\n\nasync def fetch(url, allowed, client):\n    return await fetch_file(url, allowed, client)\n",
        [
            "An explicitly listed URL can still point to a private address.",
            "Validate the target before any network operation.",
            "Use fetch_file, which enforces allow-list, address, redirect and size policy.",
        ],
    ),
    (
        "10",
        "07",
        "minimize",
        "secure",
        "Share only Granite's required brief",
        "Return just guests and date. The supplied source brief also contains private fields and the total budget.",
        "def delegate(brief):\n    # YOUR CODE HERE: this copies private information to an independent vendor.\n    return dict(brief)\n",
        'def delegate(brief):\n    return {key: brief[key] for key in ("guests", "date")}\n',
        [
            "Granite needs an attendance count and a date.",
            "Removing only password still exposes other private fields.",
            "Select an explicit allow-list of two keys.",
        ],
    ),
]

CHUNKS = """from a2a.server.agent_execution import AgentExecutor
from a2a.helpers import new_task_from_user_message, new_text_artifact_update_event, new_text_status_update_event
from a2a.types import TaskState

class SetupPlan(AgentExecutor):
    async def execute(self, context, event_queue):
        task = new_task_from_user_message(context.message)
        await event_queue.enqueue_event(task)
        for index, text in enumerate(["Microphones. ", "Projector."]):
            await event_queue.enqueue_event(new_text_artifact_update_event(
                task.id, task.context_id, "plan", text, artifact_id="setup",
                append=index > 0, last_chunk=LAST,
            ))
        await event_queue.enqueue_event(new_text_status_update_event(
            task.id, task.context_id, TaskState.TASK_STATE_COMPLETED, "Ready."
        ))

    async def cancel(self, context, event_queue):
        await event_queue.enqueue_event(new_text_status_update_event(
            context.task_id, context.context_id, TaskState.TASK_STATE_CANCELED, "Canceled."
        ))

def build():
    # YOUR CODE HERE: repair the chunk boundary above.
    return SetupPlan()
"""
TASKS.append(
    (
        "07",
        "07",
        "chunks",
        "fix",
        "Finish Brightline's streamed artifact",
        "The first artifact chunk must replace, the second must append and close, and the task must complete.",
        CHUNKS.replace("LAST", "False"),
        CHUNKS.replace("LAST", "index == 1"),
        [
            "Artifact completion and task completion are separate.",
            "Mark only the final artifact chunk as last.",
            "Set last_chunk to index == 1.",
        ],
    )
)


def main() -> None:
    for module, number, check, kind, title, scenario, starter, solution, hints in TASKS:
        folder = ROOT / "gym/tasks" / module / f"{module}-{number}_{check}"
        metadata = {
            "id": f"{module}-{number}",
            "module": module,
            "title": title,
            "type": kind,
            "level": "hard",
            "harness": "protocol",
            "check": check,
        }
        files = {
            "task.json": json.dumps(metadata, indent=2),
            "task.md": f"# {metadata['id']}: {title}\n\n{scenario}\n\n## Acceptance criteria\n\nThe trusted grader uses actual SDK routes or protobuf calls and adversarial inputs. No ports, API keys, or model are required. Your starter must fail before the fix; your solution must pass every assertion.\n\n## Spec\n\n[A2A 1.0.1](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)\n\nRun: uv run gym start {metadata['id']}, then uv run gym check {metadata['id']}.\n",
            "starter/solution.py": starter,
            "solution/solution.py": solution,
            "hints.md": "\n\n".join(f"## Hint {i}\n\n{hint}" for i, hint in enumerate(hints, 1)),
            "explanation.md": f"# Why the repair works\n\n{scenario}\n\nThe solution is checked at the actual protocol boundary. A passing happy path is insufficient: the grader also asserts task identity, trust, ownership, or transport effects relevant to this task. Read gym/protocol_checks.py after solving to inspect the acceptance checks.\n\nCommon wrong answer: changing the expected result instead of the defective boundary. Only workspace files are editable; the trusted grader remains outside the attempt.\n",
            "test_task.py": "from gym.engine import check_from_test\n\ndef test_task():\n    check_from_test(__file__)\n",
        }
        for name, content in files.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print("Wrote seven protocol-boundary tasks.")


if __name__ == "__main__":
    main()
