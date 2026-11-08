"""Author distinct full-boundary exercises, not copies of small dictionary transforms."""

import json
import textwrap

from common.config import ROOT

PREFIX = "from common.protocol import as_dict, request\nfrom common.lessons import events\n\n"
TASKS = []


def add(module, family, action, title, code, requirement, kind="build"):
    TASKS.append((module, family, action, title, textwrap.dedent(code).strip(), requirement, kind))


add(
    "02",
    "discovery",
    "interfaces",
    "Discover binding preference order",
    """
    card = (await http.get('/.well-known/agent-card.json')).json()
    return [i['protocolBinding'] for i in card['supportedInterfaces']]
""",
    "Fetch the public card and preserve the vendor's interface order.",
)
add(
    "02",
    "discovery",
    "skill",
    "Select Granite's quote contract",
    """
    card = (await http.get('/.well-known/agent-card.json')).json()
    return next(skill for skill in card['skills'] if skill['id'] == 'venues.quote')
""",
    "Find the stable skill ID; do not select by free-text instructions.",
)
add(
    "02",
    "discovery",
    "capabilities",
    "Read capability defaults",
    """
    card = (await http.get('/.well-known/agent-card.json')).json()
    cap = card['capabilities']
    return {'streaming': cap.get('streaming', False), 'push': cap.get('pushNotifications', False), 'extended': cap.get('extendedAgentCard', False)}
""",
    "Read three capability booleans, including absent protobuf defaults.",
    "fix",
)
add(
    "02",
    "discovery",
    "media",
    "Choose an advertised input representation",
    """
    card = (await http.get('/.well-known/agent-card.json')).json()
    return card['defaultInputModes']
""",
    "Read supported media types without inferring them from a filename.",
)
add(
    "02",
    "discovery",
    "security",
    "Resolve a named security requirement",
    """
    card = (await http.get('/.well-known/agent-card.json')).json()
    required = list(card['securityRequirements'][0]['schemes'])
    return {'scheme': card['securitySchemes'][required[0]]['httpAuthSecurityScheme']['scheme'], 'required': required}
""",
    "Resolve securityRequirements through securitySchemes; never treat a card as a credential.",
    "secure",
)
add(
    "02",
    "discovery",
    "validate",
    "Validate discovered ProtoJSON",
    """
    from a2a.types import AgentCard
    from google.protobuf.json_format import ParseDict
    document = (await http.get('/.well-known/agent-card.json')).json()
    parsed = ParseDict(document, AgentCard())
    return {'name': parsed.name, 'version': parsed.version}
""",
    "Parse a real card using current protobuf types, preserving identity.",
    "conformance",
)

add(
    "04",
    "client",
    "rpc",
    "Send a raw JSON-RPC quote request",
    """
    response = await http.post('/rpc', json={'jsonrpc': '2.0', 'id': 'quote', 'method': 'SendMessage', 'params': as_dict(request(brief))})
    return response.json()['result']['task']
""",
    "Build the full envelope and return the Task for the supplied brief.",
    "interop",
)
add(
    "04",
    "client",
    "rest",
    "Send the same brief over HTTP+JSON",
    """
    return (await http.post('/message:send', json=as_dict(request(brief)))).json()['task']
""",
    "Use the REST binding and read the SendMessageResponse task union.",
    "interop",
)
add(
    "04",
    "client",
    "sdk",
    "Choose a binding with the official client",
    """
    from a2a.client import ClientConfig, create_client
    from a2a.types import AgentCard
    from google.protobuf.json_format import ParseDict
    card = ParseDict((await http.get('/.well-known/agent-card.json')).json(), AgentCard())
    sdk = await create_client(card, ClientConfig(httpx_client=http, streaming=False))
    result = [as_dict(item) async for item in sdk.send_message(request(brief))][-1]
    return result['task']
""",
    "Discover first, then configure the SDK client with the provided authenticated transport.",
)
add(
    "04",
    "client",
    "poll",
    "Poll the work order you created",
    """
    task = (await http.post('/message:send', json=as_dict(request(brief)))).json()['task']
    polled = (await http.get('/tasks/' + task['id'])).json()
    return {'created': task['id'], 'polled': polled['id'], 'state': polled['status']['state']}
""",
    "Keep the returned task ID; never poll using messageId or contextId.",
    "fix",
)
add(
    "04",
    "client",
    "missing",
    "Handle an unknown task without retrying",
    """
    response = await http.get('/tasks/never-created')
    return {'status': response.status_code, 'reason': response.json()['error']['details'][0]['reason']}
""",
    "Recognize TASK_NOT_FOUND and preserve its transport status.",
    "conformance",
)
add(
    "04",
    "client",
    "correlation",
    "Separate exchange and work-order identities",
    """
    response = (await http.post('/rpc', json={'jsonrpc': '2.0', 'id': 'client-' + str(brief['guests']), 'method': 'SendMessage', 'params': as_dict(request(brief))})).json()
    task = response['result']['task']
    return {'rpc_id': response['id'], 'task_id': task['id'], 'context_id': task['contextId']}
""",
    "Return the three independent identities from a real exchange.",
    "fix",
)

add(
    "05",
    "lifecycle",
    "resume",
    "Continue Saffron's stored work order",
    """
    message = request({'dietary': brief['dietary']}, task_id=previous['id'], context_id=previous['contextId'])
    return (await http.post('/message:send', json=as_dict(message))).json()['task']
""",
    "The provided previous Task is paused. Complete it without resending its guest count.",
    "fix",
)
add(
    "05",
    "lifecycle",
    "cancel",
    "Cancel paused catering work",
    """
    return (await http.post('/tasks/' + previous['id'] + ':cancel', json={})).json()
""",
    "Cancel the existing task and verify the persisted terminal state.",
)
add(
    "05",
    "lifecycle",
    "history",
    "Request bounded task history",
    """
    follow = request({'dietary': brief['dietary']}, task_id=previous['id'], context_id=previous['contextId'])
    await http.post('/message:send', json=as_dict(follow))
    return (await http.get('/tasks/' + previous['id'], params={'historyLength': 1})).json()
""",
    "Continue a conversation, then return its task with exactly one history message.",
    "conformance",
)
add(
    "05",
    "lifecycle",
    "list",
    "Page through owner-scoped tasks",
    """
    for _ in range(2):
        await http.post('/message:send', json=as_dict(request(brief)))
    return (await http.get('/tasks', params={'pageSize': 1})).json()
""",
    "Create additional quotes and return a one-task page with a continuation token.",
)
add(
    "05",
    "lifecycle",
    "auth",
    "Pause for out-of-band authorization",
    """
    return (await http.post('/message:send', json=as_dict(request({**brief, 'require_partner': True})))).json()['task']
""",
    "Ask for a partner-only action. Observe auth-required without placing a credential in the message.",
    "secure",
)
add(
    "05",
    "lifecycle",
    "rejected",
    "Reject an impossible catering request",
    """
    return (await http.post('/message:send', json=as_dict(request({**brief, 'guests': 0})))).json()['task']
""",
    "Exercise a business rejection; do not confuse it with an HTTP authorization error.",
    "conformance",
)

STREAM = "rows = events((await http.post('/message:stream', json=as_dict(request(brief)))).text)\n"
add(
    "07",
    "stream",
    "status",
    "Read state transitions from a real stream",
    STREAM
    + "return [e['task']['status']['state'] if 'task' in e else e['statusUpdate']['status']['state'] for e in rows if 'task' in e or 'statusUpdate' in e]",
    "Distinguish the initial task snapshot from subsequent status updates.",
)
add(
    "07",
    "stream",
    "chunks",
    "Assemble an AV artifact across chunks",
    STREAM
    + """
text = ''
for event in rows:
    update = event.get('artifactUpdate', {})
    if update.get('artifact', {}).get('artifactId') == 'plan':
        chunk = ''.join(p.get('text', '') for p in update['artifact']['parts'])
        text = text + chunk if update.get('append', False) else chunk
return text
""",
    "Apply replace/append semantics, ignoring other artifacts.",
    "fix",
)
add(
    "07",
    "stream",
    "flags",
    "Audit AV chunk termination",
    STREAM
    + "return [[e['artifactUpdate'].get('append', False), e['artifactUpdate'].get('lastChunk', False)] for e in rows if e.get('artifactUpdate', {}).get('artifact', {}).get('artifactId') == 'plan']",
    "Return append/lastChunk pairs for the three plan chunks; task completion is separate.",
    "conformance",
)
add(
    "07",
    "stream",
    "identity",
    "Keep task identity across all event variants",
    STREAM
    + """
task = rows[0]['task']
updates = [next(iter(e.values())) for e in rows[1:]]
return {'same_task': all(e['taskId'] == task['id'] for e in updates), 'same_context': all(e['contextId'] == task['contextId'] for e in updates), 'events': len(rows)}
""",
    "Use the actual snapshot as the identity source and inspect every following event.",
    "conformance",
)
add(
    "07",
    "stream",
    "quote",
    "Separate the final data artifact from progress",
    STREAM
    + "return next(e['artifactUpdate']['artifact']['parts'][0]['data'] for e in rows if e.get('artifactUpdate', {}).get('artifact', {}).get('artifactId') == 'quote')",
    "Return only the structured quote, never status text or the setup-plan chunks.",
)
add(
    "07",
    "stream",
    "snapshot",
    "Reconcile streamed chunks with stored state",
    STREAM
    + """
task = (await http.get('/tasks/' + rows[0]['task']['id'])).json()
return {'state': task['status']['state'], 'artifact_ids': sorted(a['artifactId'] for a in task['artifacts'])}
""",
    "Poll after completion and verify the stored artifacts are assembled once each.",
    "interop",
)

add(
    "13",
    "security",
    "anonymous",
    "Keep work endpoints authenticated",
    "return (await http.post('/message:send', json=as_dict(request(brief)))).status_code",
    "Probe with no credentials and return the denial status.",
    "secure",
)
add(
    "13",
    "security",
    "owner",
    "Attack a different caller's task ID",
    "return (await http.get('/tasks/' + previous['id'], headers={'Authorization': 'Bearer stranger'})).status_code",
    "The provided task belongs to owner. Confirm stranger cannot read it.",
    "secure",
)
add(
    "13",
    "security",
    "tenant",
    "Reject a forged tenant header",
    "return (await http.post('/message:send', headers={'Authorization': 'Bearer owner', 'X-Tenant': 'other'}, json=as_dict(request(brief)))).status_code",
    "Authenticate correctly but claim another tenant; the claim must not grant access.",
    "secure",
)
add(
    "13",
    "security",
    "extended_denied",
    "Enforce the extended-card partner scope",
    "return (await http.get('/extendedAgentCard', headers={'Authorization': 'Bearer owner'})).status_code",
    "A valid general token must not reveal the partner-only card.",
    "secure",
)
add(
    "13",
    "security",
    "extended_partner",
    "Discover the authorized partner skill",
    """
document = (await http.get('/extendedAgentCard', headers={'Authorization': 'Bearer partner'})).json()
return next(s['id'] for s in document['skills'] if s['id'] == 'travel.partner_quote')
""",
    "Use an authorized partner token and read the extended skill contract.",
)
add(
    "13",
    "security",
    "body_secret",
    "Reject a credential smuggled in task data",
    "return (await http.post('/message:send', json=as_dict(request({**brief, 'token': 'owner'})))).status_code",
    "Putting a credential into a message must never authenticate the caller.",
    "secure",
)

for action, title, method, params in [
    ("method", "Reject an unknown operation", "InventedOperation", "{}"),
    ("missing", "Return TaskNotFound for an unknown ID", "GetTask", "{'id': 'never-created'}"),
    ("media", "Reject an unsupported Part media type", "SendMessage", "body"),
    ("version", "Reject an unsupported protocol version", "SendMessage", "as_dict(request(brief))"),
]:
    setup = (
        "body = as_dict(request(brief))\nbody['message']['parts'][0]['mediaType'] = 'application/x-unsupported-tck-type'\n"
        if action == "media"
        else ""
    )
    header = ", headers={'A2A-Version': '99.0'}" if action == "version" else ""
    add(
        "16",
        "conformance",
        action,
        title,
        setup
        + f"response = await http.post('/rpc', json={{'jsonrpc': '2.0', 'id': 1, 'method': '{method}', 'params': {params}}}{header})\nreturn response.json()['error']['code']",
        "Use the real protocol boundary and return its JSON-RPC error code.",
        "conformance",
    )
add(
    "16",
    "conformance",
    "parse",
    "Separate parse errors from invalid parameters",
    "return (await http.post('/rpc', content='{not-json', headers={'Content-Type': 'application/json'})).json()['error']['code']",
    "Send malformed JSON and observe a parser error before any business work.",
    "fix",
)
add(
    "16",
    "conformance",
    "rest_media",
    "Verify the HTTP error representation",
    "return (await http.get('/tasks/never-created')).headers['content-type']",
    "Read the media type on an actual A2A error response.",
    "conformance",
)


FILES = "task = (await http.post('/message:send', json=as_dict(request({**brief, 'include_files': True})))).json()['task']\n"
add(
    "06",
    "parts",
    "floor_plan",
    "Receive Granite's real image artifact",
    FILES
    + "return next(p for a in task['artifacts'] for p in a['parts'] if p.get('mediaType') == 'image/svg+xml')",
    "Return the raw SVG image Part, preserving its filename and media type.",
)
add(
    "06",
    "parts",
    "data",
    "Read and validate a structured quote",
    FILES + "return next(p['data'] for a in task['artifacts'] for p in a['parts'] if 'data' in p)",
    "Select the structured-data Part without assuming the first file is a quote.",
)
add(
    "06",
    "parts",
    "artifact_ids",
    "Keep independent deliverables separate",
    FILES + "return sorted(a['artifactId'] for a in task['artifacts'])",
    "Return stable artifact IDs for the quote and floor plan, not filenames.",
    "conformance",
)
add(
    "06",
    "parts",
    "raw_input",
    "Attach inline artwork as a raw Part",
    """
from a2a.types import Part
message = request(brief)
message.message.parts.append(Part(raw=b'synthetic-artwork', filename='artwork.bin', media_type='application/octet-stream'))
return (await http.post('/message:send', json=as_dict(message))).json()['task']
""",
    "Send a data Part and an inline raw Part in one message using protobuf serialization.",
    "interop",
)
add(
    "06",
    "parts",
    "unsupported",
    "Negotiate supported file media types",
    """
message = as_dict(request(brief))
message['message']['parts'][0]['mediaType'] = 'application/x-private-format'
return (await http.post('/message:send', json=message)).status_code
""",
    "Exercise a server rejection for an unsupported message-part media type.",
    "conformance",
)
add(
    "06",
    "parts",
    "multi_part",
    "Receive Saffron's data and PDF together",
    FILES
    + "parts = task['artifacts'][0]['parts']\nreturn {'data': next(p['data'] for p in parts if 'data' in p), 'file': next(p for p in parts if p.get('mediaType') == 'application/pdf')}",
    "Return the structured quote and valid PDF file from the same artifact.",
)

PUSH_PATH = "path = '/tasks/' + previous['id'] + '/pushNotificationConfigs'\n"
add(
    "07",
    "push",
    "create",
    "Register an approved callback",
    PUSH_PATH
    + "return (await http.post(path, json={'taskId': previous['id'], 'id': 'planner', 'url': previous['url']})).json()",
    "Create one named TaskPushNotificationConfig on an existing task.",
)
add(
    "07",
    "push",
    "get",
    "Retrieve one callback configuration",
    PUSH_PATH + "return (await http.get(path + '/planner')).json()",
    "Read the registered planner callback using its task ID and configuration ID.",
    "interop",
)
add(
    "07",
    "push",
    "list",
    "Inspect all task callback registrations",
    PUSH_PATH + "return (await http.get(path)).json()",
    "List the callback collection and preserve the configs response field.",
    "conformance",
)
add(
    "07",
    "push",
    "delete",
    "Remove a callback without canceling work",
    PUSH_PATH + "return (await http.delete(path + '/planner')).status_code",
    "Delete the registration; the task itself must remain accessible.",
    "fix",
)
add(
    "07",
    "push",
    "ssrf",
    "Reject a metadata-service callback",
    PUSH_PATH
    + "return (await http.post(path, json={'taskId': previous['id'], 'id': 'planner', 'url': 'https://169.254.169.254/latest'})).status_code",
    "The callback allow-list must reject the internal target before any delivery.",
    "secure",
)
add(
    "07",
    "push",
    "delivery",
    "Deliver completion through an authenticated outbox",
    """
message = request(brief, task_id=previous['id'], context_id=previous['contextId'])
return (await http.post('/message:send', json=as_dict(message))).json()['task']
""",
    "Resume the paused task. The durable kit must deliver a signed completion callback to its verified receiver.",
)


def main():
    counters = {}
    for module, family, action, title, code, requirement, kind in TASKS:
        counters[module] = counters.get(module, 19) + 1
        identifier = f"{module}-{counters[module]}"
        folder = ROOT / "gym/tasks" / module / f"{identifier}_{family}_{action}"
        solution = (
            PREFIX
            + "async def exercise(http, brief, previous):\n"
            + textwrap.indent(code, "    ")
            + "\n"
        )
        metadata = {
            "id": identifier,
            "module": module,
            "title": title,
            "type": kind,
            "level": "hard",
            "harness": "protocol",
            "check": f"boundary:{family}:{action}",
            "feature": family,
        }
        files = {
            "task.json": json.dumps(metadata, indent=2),
            "task.md": f"# {identifier}: {title}\n\nMaplewood is upgrading its {family} boundary. {requirement}\n\nImplement async exercise(http, brief, previous). The supplied client is in-process and carries the appropriate fixture credentials unless this is an authorization attack. Read the original brief dynamically: the grader varies guest counts. Return the result described below.\n\n## Acceptance criteria\n\n{requirement} The grader performs actual SDK requests, checks resulting state, and rejects the starter. It uses no network or API keys. Read [the trusted acceptance contract](../../../../gym/boundary_checks.py) for the exact return shape; do not edit it.\n\n## Spec\n\n[A2A normative operations and types](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).\n\nRun uv run gym start {identifier}, then uv run gym check {identifier}.\n",
            "starter/solution.py": PREFIX
            + "async def exercise(http, brief, previous):\n    # Repair the missing protocol exchange and return the required observation.\n    return {}\n",
            "solution/solution.py": solution,
            "test_task.py": "from gym.engine import check_from_test\n\ndef test_task():\n    check_from_test(__file__)\n",
            "hints.md": f"## Hint 1\n\n{requirement}\n\n## Hint 2\n\nUse the provided http client and the current A2A operation names. Preserve IDs returned by the server.\n\n## Hint 3\n\nThe reference uses {family} data from actual responses. Inspect the module's wire capture and match its ProtoJSON field names.\n",
            "explanation.md": f"# Why this works\n\n{requirement}\n\nThe request crosses the official SDK boundary. The result is an observation of server behavior, not a local prediction or a fabricated response. Repeated tests vary the supplied brief to catch hard-coded counts. Wrong approaches include using contextId as task ID, omitting the response union, inventing snake_case JSON field names, or moving credentials into a Part.\n\n## Reference implementation\n\n~~~python\n{solution}~~~\n",
        }
        for name, content in files.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {len(TASKS)} distinct full-boundary tasks.")


if __name__ == "__main__":
    main()
