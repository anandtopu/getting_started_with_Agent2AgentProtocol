"""Generate reference tables from the checked course catalog and installed protobuf."""

import json

from a2a.types import a2a_pb2

from common.config import ROOT


def write(name: str, text: str) -> None:
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


TERMS = {
    "A2A": "Agent2Agent: a shared protocol for independently operated agents to exchange work.",
    "Agent": "A program that can perform work or decide how to pursue a request.",
    "Client": "The side that initiates a protocol operation.",
    "Server": "The side that accepts requests and returns results.",
    "Agent Card": "A machine-readable description of an agent's identity, interfaces, skills and security.",
    "Discovery": "Finding and reading an agent's card before choosing how to contact it.",
    "Registry": "A directory of agent locations; membership alone does not establish trust.",
    "Skill": "A named, documented capability offered by an agent.",
    "Capability": "A declared protocol feature such as streaming or push notifications.",
    "Interface": "An endpoint combined with its binding, protocol version and optional tenant.",
    "Message": "One communication containing a role, identifier and parts.",
    "Message ID": "An identifier assigned by a message's creator, distinct from a request or task ID.",
    "Part": "One content item: text, raw bytes, URL or structured JSON value.",
    "Artifact": "A named deliverable produced by a task.",
    "Task": "Tracked work with an identifier, state, optional history and artifacts.",
    "Task ID": "The server-assigned identifier used to inspect, continue or cancel work.",
    "Context ID": "A server-scoped grouping of related interactions, analogous to a project folder.",
    "Submitted": "The task has been acknowledged.",
    "Working": "The agent is processing the task.",
    "Input-required": "Work is interrupted until the client supplies information.",
    "Auth-required": "Work is interrupted until external authorization requirements are satisfied.",
    "Completed": "The task finished successfully and cannot be restarted.",
    "Failed": "The task finished unsuccessfully because execution failed.",
    "Rejected": "The agent declined to perform the work.",
    "Canceled": "The task stopped before normal completion following cancellation.",
    "Terminal state": "A state from which the same task does not resume.",
    "Interrupted state": "A paused state from which the task may continue.",
    "HTTP": "A request/response web protocol with methods, headers, status codes and a body.",
    "HTTPS": "HTTP protected by TLS encryption and peer authentication.",
    "URL": "A location identifying a resource and how to access it.",
    "URI": "An identifier that may identify a resource without providing a fetchable location.",
    "Endpoint": "An address accepting a particular kind of request.",
    "Header": "Transport metadata such as authorization or a content type.",
    "Body": "The content carried by an HTTP request or response.",
    "Status code": "A transport result such as 200 success, 401 unauthenticated or 404 not found.",
    "JSON": "A text representation of objects, arrays, strings, numbers, booleans and null.",
    "JSON-RPC": "A remote procedure call envelope containing a method, parameters and correlation ID.",
    "gRPC": "A remote procedure call system commonly using protobuf over HTTP/2.",
    "Protobuf": "A schema language and binary serialization system.",
    "ProtoJSON": "The defined JSON representation of protobuf messages, including field and enum names.",
    "Binding": "A mapping of abstract protocol operations onto a concrete transport.",
    "SSE": "Server-Sent Events: named or data events sent through a long-lived HTTP response.",
    "Streaming": "Receiving progress or partial output before the work is finished.",
    "Polling": "Repeatedly asking for the current state.",
    "Webhook": "An HTTP callback initiated by a remote service.",
    "Push notification": "An asynchronous update delivered to a configured receiver.",
    "Chunk": "One portion of an artifact delivered incrementally.",
    "Append": "An instruction to add content to an existing artifact with the same identifier.",
    "Last chunk": "The final portion of one artifact; it does not by itself finish the task.",
    "Authentication": "Checking who a caller or service is.",
    "Authorization": "Checking what an authenticated identity may do.",
    "Bearer token": "A credential whose holder can present it for access.",
    "API key": "A service credential provisioned outside the protocol.",
    "OAuth": "A framework for obtaining delegated access to protected resources.",
    "OpenID Connect": "An identity layer and discovery conventions built on OAuth.",
    "JWT": "A compact claims format that must be verified before its claims are trusted.",
    "JWS": "A standard for signing a payload and associated protected headers.",
    "JWKS": "A JSON set of public keys, which must itself come from a trusted source.",
    "JCS": "JSON canonicalization: a deterministic byte representation for signing.",
    "TLS": "Transport Layer Security: encryption and peer authentication for a connection.",
    "mTLS": "TLS that also authenticates the client using a certificate.",
    "PKCE": "A proof mechanism that helps protect OAuth authorization codes from interception.",
    "Scope": "A named permission associated with a credential.",
    "Tenant": "An application routing or isolation partition; a request field is not authorization.",
    "SSRF": "Server-side request forgery: inducing a server to contact an unintended destination.",
    "DNS rebinding": "Changing a hostname's resolved address between validation and connection.",
    "Replay attack": "Reusing a previously valid message to trigger processing again.",
    "Nonce": "A value intended to be used once, useful when detecting replay.",
    "HMAC": "A message authentication code using a shared secret.",
    "Prompt injection": "Untrusted content attempting to act as instructions to a model or agent.",
    "Confused deputy": "A more privileged service being tricked into using its authority for someone else.",
    "Allow-list": "An explicit set of destinations or actions the application permits.",
    "LLM": "A language model that predicts output from supplied context.",
    "Tool calling": "A model requesting application code to invoke a named function with arguments.",
    "MCP": "Model Context Protocol: connecting a host to tools and resources.",
    "Async": "Cooperative execution that yields while awaiting work.",
    "ASGI": "A Python interface between asynchronous web applications and their servers.",
    "Coroutine": "An asynchronous function's resumable computation.",
    "Timeout": "A bound on waiting; it does not prove remote work was undone.",
    "Retry": "A new attempt after a failure or uncertain result.",
    "Idempotency": "An application property that repeated requests do not repeat a side effect.",
    "Compensation": "A new business action that offsets an earlier successful action.",
    "Trace": "Related operation records showing work across components.",
    "Span": "One timed operation inside a trace.",
    "Trace context": "Transported identifiers connecting spans across services.",
    "Conformance": "Agreement with specified protocol requirements.",
    "TCK": "Technology Compatibility Kit: the project's official compatibility tests.",
    "Evaluation": "Checking whether a result satisfies business requirements.",
    "Golden scenario": "A fixed input with expected delegations, states and deliverables.",
    "Extension": "An identified addition to a protocol contract, declared and activated explicitly.",
    "Pagination": "Returning a bounded portion of a collection with a token for the next portion.",
    "Persistent store": "Storage that survives a process restart.",
    "Replica": "Another running copy of a service.",
    "Load balancer": "A component that distributes requests across service copies.",
    "Container": "A packaged process environment; it is not by itself a security or scaling strategy.",
    "ADR": "Architecture decision record: context, alternatives, decision and consequences.",
}


def main() -> None:
    modules = json.loads((ROOT / "common/course_catalog.json").read_text())
    rows = []
    for module in modules:
        folder = (
            "modules/bonus/" if module["id"].startswith("B") else "modules/"
        ) + f"{module['id']}_{module['slug']}"
        rows.append(
            f"| [{module['id']}: {module['title']}]({folder}/README.md) | {module['tier']} | 90 min plus practice |"
        )
    schedule = """## Three-week intensive

Plan 3â€“4 hours per study day, plus extra capstone time. Every day: predict one
result before running it, finish the assigned gym checks, and review yesterday's mistakes.

| Days | Work |
|---|---|
| 1â€“3 | 00â€“02: setup, objects, discovery |
| 4â€“6 | 03â€“05: server, client, lifecycle |
| 7â€“9 | 06â€“08: parts, streams and bindings; Tier 1 checkpoint |
| 10â€“13 | 09â€“12: models, orchestration, framework boundaries and MCP |
| 14â€“16 | 13â€“15: authentication, card trust and security audit |
| 17â€“20 | 16â€“19: tests, traces, extensions and deployment |
| 21 | 20: architecture review and flagship capstone plan |

## Six-week part-time

Plan 8â€“12 hours weekly. Study four days, practice on two days, then review.
On every study day run gym next; once a module is finished, use gym drill for review.

| Week | Modules | Practice/checkpoint |
|---|---|---|
| 1 | 00â€“03 | Discover and serve a deterministic vendor |
| 2 | 04â€“08 | Complete Tier 1 with continuation, chunks and protobuf |
| 3 | 09â€“12 | Script decisions, delegate safely and compare tool boundaries |
| 4 | 13â€“15 | Audit identity, authorization, signatures and untrusted content |
| 5 | 16â€“18 | Contract tests, golden scenarios and version negotiation |
| 6 | 19â€“20 | Deployment review and capstone presentation |

## Tier checkpoints

- **Tier 1:** You can explain a captured request, preserve a paused task, assemble
  chunks and compare bindings. Demonstrate tasks 02-01, 05-02, 07-01 and 08-05.
- **Tier 2:** You can validate tool decisions, minimize delegation and compare
  framework boundaries. Demonstrate 09-01, 10-02, 11-05 and 12-06.
- **Tier 3:** You can reject unauthorized partner access, cross-owner reads and
  unsafe destinations. Demonstrate 13-05, 14-02 and 15-05; review the security rubric.
- **Tier 4:** You can explain a trace, test a golden scenario, negotiate an extension
  and design compensation. Demonstrate 16-05, 17-01, 18-05, 19-02 and 20-06.

Passing a small exercise is evidence for one skill, not proof of production readiness.
Use the capstone acceptance criteria and the verification notes to identify remaining work.
"""
    write(
        "LEARNING_PATH.md",
        "# Learning path\n\nFollow modules in order, or use gym list to target a skill.\n\n| Module | Tier | Time |\n|---|---|---|\n"
        + "\n".join(rows)
        + "\n\n"
        + schedule,
    )
    write(
        "docs/GLOSSARY.md",
        "# Glossary\n\n"
        + "\n\n".join(f"## {term}\n\n{definition}" for term, definition in TERMS.items()),
    )
    packages = json.loads((ROOT / "docs/package_observations.json").read_text())
    version_table = "\n".join(
        f"| {name} | {value['version']} | [PyPI]({value['source']}) |"
        for name, value in packages.items()
    )
    write(
        "docs/PACKAGE_VERSIONS.md",
        "# Package versions checked on 2026-11-07\n\nThese are registry observations, not a claim that all packages can share one environment. The actual selected versions are locked in uv.lock; optional incompatible frameworks need isolated environments.\n\n| Package | Observed version | Source |\n|---|---|---|\n"
        + version_table
        + "\n\nnpm: @a2a-js/sdk 1.3.0, TypeScript 7.0.2, tsx 4.23.15, Express 5.3.0; exact resolution is in package-lock.json.",
    )
    service = a2a_pb2.DESCRIPTOR.services_by_name["A2AService"]
    operations = "\n".join(
        f"| {method.name} | {method.input_type.name} | {method.output_type.name} | {'stream' if method.server_streaming else 'unary'} |"
        for method in service.methods
    )
    objects = "\n".join(
        f"| {name} | " + ", ".join(f.json_name for f in descriptor.fields) + " |"
        for name, descriptor in a2a_pb2.DESCRIPTOR.message_types_by_name.items()
    )
    write(
        "docs/PROTOCOL_GUIDE.md",
        "# Protocol guide\n\nA2A 1.0.1 uses one normative protobuf schema across JSON-RPC, HTTP+JSON and gRPC. The tables below are generated from the installed 1.3.0 SDK descriptor, checked against the versioned protocol definition.\n\n## Follow one request\n\n1. Fetch the Agent Card at /.well-known/agent-card.json.\n2. Choose a supported interface and obtain its required credentials separately.\n3. Send a Message inside SendMessageRequest with A2A-Version: 1.0.\n4. Receive a Message or a Task. For a task, preserve its IDs and inspect status and artifacts.\n5. If interrupted, provide the missing input or obtain authorization outside the message payload.\n6. Treat completed, failed, canceled and rejected tasks as terminal.\n\n## Operations\n\n| Operation | Request | Response | Form |\n|---|---|---|---|\n"
        + operations
        + "\n\n## Objects and exact JSON fields\n\n| Object | JSON fields |\n|---|---|\n"
        + objects
        + "\n\n## Actual examples\n\n- [JSON-RPC request and response](../modules/01_how_a2a_works/wire/01_jsonrpc.jsonl)\n- [HTTP+JSON](../modules/08_bindings/wire/02_rest.jsonl)\n- [Protobuf service boundary](../modules/08_bindings/wire/03_grpc.jsonl)\n- [SSE events](../modules/07_streaming_push/wire/01_stream.jsonl)\n- [Push configuration and deliveries](../modules/07_streaming_push/wire/03_push.jsonl)\n- [Task continuation](../modules/05_task_lifecycle/wire/02_resume.jsonl)\n\nThese captures cover the implemented labs, not every possible object or operation variant.\n\nSources: [normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto), [binding rules](https://a2a-protocol.org/v1.0.1/specification/).",
    )
    for tier in range(1, 5):
        topics = [m for m in modules if m["tier"] == tier]
        write(
            f"cheatsheets/tier_{tier}.md",
            f"# Tier {tier}: desk reference\n\n"
            + "\n\n".join(f"**{m['title']}** â€” {m['idea']}" for m in topics)
            + "\n\nPractice: uv run gym list --module NN; uv run gym next; uv run gym drill.",
        )
    write(
        "cheatsheets/protocol.md",
        "# A2A protocol at a glance\n\nCard â†’ interface â†’ authenticated request â†’ Message or Task â†’ status and artifacts.\n\n- Interface version: 1.0. Specification release: 1.0.1.\n- Bindings: JSONRPC, HTTP+JSON, GRPC.\n- Parts: text, raw, url or data; exactly one content alternative.\n- States: submitted, working; interrupted input-required/auth-required; terminal completed/failed/canceled/rejected. Wire values use TASK_STATE_ prefixes.\n- New task streams start with Task; direct-message streams contain one Message.\n- Chunk flags concern an artifact; task state concerns the work order.\n- Keep tokens in headers; validate destinations and outputs.\n\nSee the [operation table](../docs/PROTOCOL_GUIDE.md).",
    )
    print(
        f"Wrote learning schedules, {len(TERMS)} glossary terms, version table and descriptor-based protocol reference."
    )


if __name__ == "__main__":
    main()
