"""Author six distinct acceptance exercises for each advanced protocol feature group."""

import json
import textwrap

from common.config import ROOT

TASKS = []


def add(module, family, action, title, code, requirement, kind="build"):
    TASKS.append((module, family, action, title, textwrap.dedent(code).strip(), requirement, kind))


add(
    "14",
    "trust",
    "verify",
    "Verify a pinned vendor signature",
    """
from common.security import verify_card
return verify_card(context['card'], context['keys'])['name']
""",
    "Verify cryptographic integrity before accepting the vendor identity.",
    "secure",
)
for action, title in [
    ("tamper", "Reject an injected skill description"),
    ("unknown", "Reject a self-appointed signing key"),
]:
    add(
        "14",
        "trust",
        action,
        title,
        """
from common.security import verify_card
try:
    verify_card(context['card'], context['keys'])
    return True
except ValueError:
    return False
""",
        "Return whether the supplied card is valid under the operator's pinned keys. The fixture attacks this trust boundary.",
        "secure",
    )
add(
    "14",
    "trust",
    "canonical",
    "Canonicalize before signing",
    """
from common.security import sign_card
document = dict(reversed(list(context['card'].items())))
return sign_card(document, context['private'], context['kid'])
""",
    "Sign the reordered document. Exclude existing signatures and produce the same JCS signature.",
    "conformance",
)
add(
    "14",
    "trust",
    "rotation",
    "Keep valid keys during rotation overlap",
    """
from common.security import verify_card
from common.card_trust import trusted_jwks
ring, clock = context['ring'], context['clock']
old = ring.card()
clock[0] = 101
verify_card(old, trusted_jwks(ring.public_keys()))
clock[0] = 132
try:
    verify_card(old, trusted_jwks(ring.public_keys()))
    expired = True
except ValueError:
    expired = False
return {'overlap': True, 'expired': expired}
""",
    "Accept the old signature during overlap and reject it after retirement.",
)
add(
    "14",
    "trust",
    "revocation",
    "Reject a revoked card key",
    """
from common.security import verify_card
from common.card_trust import trusted_jwks
ring = context['ring']
old = ring.card()
ring.revoke(ring.current)
try:
    verify_card(old, trusted_jwks(ring.public_keys()))
    return True
except ValueError:
    return False
""",
    "A previously valid card must fail once its signing key is revoked.",
    "secure",
)

add(
    "08",
    "grpc",
    "send",
    "Send a protobuf request to Inkwell",
    """
from common.protocol import request, as_dict
return as_dict(await context['service'].unary('SendMessage', request(context['brief'])))
""",
    "Use the official gRPC service with the supplied brief; return ProtoJSON for inspection.",
    "interop",
)
for action, typename, operation in [
    ("get", "GetTaskRequest", "GetTask"),
    ("cancel", "CancelTaskRequest", "CancelTask"),
]:
    add(
        "08",
        "grpc",
        action,
        f"Call {operation} over gRPC",
        f"from a2a.types import {typename}\nfrom common.protocol import as_dict\nreturn as_dict(await context['service'].unary('{operation}', {typename}(id=context['task'].id)))",
        "Use a typed request and the existing work-order ID.",
        "interop",
    )
add(
    "08",
    "grpc",
    "list",
    "List tasks through protobuf",
    """
from a2a.types import ListTasksRequest
from common.protocol import as_dict
return as_dict(await context['service'].unary('ListTasks', ListTasksRequest(page_size=1)))
""",
    "Request a one-item page through the same authenticated service boundary.",
    "conformance",
)
add(
    "08",
    "grpc",
    "stream",
    "Inspect the gRPC stream union",
    """
from common.protocol import request
return [event.WhichOneof('payload') async for event in context['service'].stream(request(context['brief']))]
""",
    "Identify the initial Task and final status update without assuming SSE framing.",
    "interop",
)
add(
    "08",
    "grpc",
    "version",
    "Read advertised gRPC protocol compatibility",
    """
from agents.catalog import card
identity = card('print', grpc_only=True)
interface = next(i for i in identity.supported_interfaces if i.protocol_binding == 'GRPC')
return interface.protocol_version
""",
    "Read the advertised wire version instead of using the SDK package version.",
    "conformance",
)

for action, title, headers in [
    ("optional", "Omit an optional extension", "{}"),
    ("negotiated", "Activate the quote extension", "{'A2A-Extensions': context['extension']}"),
    ("required_missing", "Reject an unmet required extension", "{}"),
    (
        "required_present",
        "Satisfy a required extension",
        "{'A2A-Extensions': context['extension']}",
    ),
    ("unsupported_version", "Reject unsupported protocol negotiation", "{'A2A-Version': '99.0'}"),
]:
    code = f"from common.protocol import request, as_dict\nresponse = await context['http'].post('/message:send', json=as_dict(request(context['brief'])), headers={headers})\n"
    code += (
        "return response.json()['task']['artifacts'][0].get('extensions', [])"
        if action in {"optional", "negotiated"}
        else "return response.status_code"
    )
    add(
        "18",
        "extensions",
        action,
        title,
        code,
        "Observe negotiation at the A2A request boundary; the card declaration alone does not activate an extension.",
        "conformance",
    )
add(
    "18",
    "extensions",
    "declared",
    "Discover the structured-quote extension",
    """
card = (await context['http'].get('/.well-known/agent-card.json')).json()
return card['capabilities']['extensions'][0]['uri']
""",
    "Read the extension URI from the public card and preserve its versioned identity.",
)

SAVE = "await context['two'].save(context['task'], event=context['event'], prev=None, prev_version=context['version'], context=context['call'])"
add(
    "19",
    "persistence",
    "reload",
    "Load a task through another replica",
    "return (await context['two'].get(context['task'].id, context['call'])).task.id",
    "Read the committed task from an independent database connection.",
)
add(
    "19",
    "persistence",
    "stale",
    "Reject a stale task writer",
    "from a2a.server.cluster.task_store import ConcurrentTaskModificationError\n"
    + SAVE
    + "\ntry:\n    "
    + SAVE
    + "\n    return False\nexcept ConcurrentTaskModificationError:\n    return True",
    "Write once, then retry with the old version token and detect the conflict.",
    "fix",
)
add(
    "19",
    "persistence",
    "replay",
    "Recover an event before publication",
    """
from a2a.server.cluster.version import TaskVersion
stream = context['two'].subscribe(context['task'].id, after=TaskVersion.MISSING)
try:
    return (await anext(stream)).event.task_id
finally:
    await stream.aclose()
""",
    "Read the durable journal even though the first replica never called publish.",
)
add(
    "19",
    "persistence",
    "lease",
    "Fence an expired delivery worker",
    """
old = await context['one'].claim(now=100, seconds=5)
new = await context['two'].claim(now=106)
return [await context['one'].acknowledge(old, True, now=107), await context['two'].acknowledge(new, True, now=107)]
""",
    "Only the current lease holder may acknowledge a delivery after recovery.",
    "secure",
)
add(
    "19",
    "persistence",
    "budget",
    "Share a request budget across replicas",
    """
accepted = 0
for index in range(8):
    store = context['one'] if index % 2 else context['two']
    accepted += await store.allow('maplewood:planner', now=100, limit=3)
return accepted
""",
    "Two replicas together must allow only three requests in the same fixed window.",
    "secure",
)
add(
    "19",
    "persistence",
    "atomic",
    "Inspect the atomic event and outbox commit",
    """
from sqlalchemy import select, func
store = context['two']
async with store.engine.connect() as connection:
    return [(await connection.execute(select(func.count()).select_from(table))).scalar_one() for table in (store.events, store.outbox)]
""",
    "A persisted event and its configured delivery must both be visible after one commit.",
    "conformance",
)


def main():
    counters = {}
    for module, family, action, title, code, requirement, kind in TASKS:
        counters[module] = counters.get(module, 39) + 1
        identifier = f"{module}-{counters[module]}"
        folder = ROOT / "gym/tasks" / module / f"{identifier}_{family}_{action}"
        solution = "async def exercise(context):\n" + textwrap.indent(code, "    ") + "\n"
        metadata = {
            "id": identifier,
            "module": module,
            "title": title,
            "type": kind,
            "level": "hard",
            "harness": "protocol",
            "check": f"advanced:{family}:{action}",
            "feature": family,
        }
        files = {
            "task.json": json.dumps(metadata, indent=2),
            "task.md": f"# {identifier}: {title}\n\nMaplewood needs this {family} guarantee: {requirement}\n\nImplement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.\n\n## Acceptance criteria\n\n{requirement} No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.\n\n## Spec\n\n[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).\n\nRun uv run gym start {identifier}, then uv run gym check {identifier}.\n",
            "starter/solution.py": "async def exercise(context):\n    # Implement the required boundary interaction and return its observation.\n    return None\n",
            "solution/solution.py": solution,
            "test_task.py": "from gym.engine import check_from_test\n\ndef test_task():\n    check_from_test(__file__)\n",
            "hints.md": f"## Hint 1\n\n{requirement}\n\n## Hint 2\n\nThe supplied context contains the trusted objects. Preserve IDs, ownership, versions and configured trust anchors.\n\n## Hint 3\n\nRead the fixture's assertion and call the confirmed SDK or course API that enforces this boundary. Catch the expected rejection, not every exception.\n",
            "explanation.md": f"# Why this works\n\n{requirement}\n\nThe exercise uses real {family} objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.\n\n~~~python\n{solution}~~~\n",
        }
        for name, content in files.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {len(TASKS)} advanced boundary tasks.")


if __name__ == "__main__":
    main()
