**Network and Concierge version 07:** what's new — streaming and push notifications.

# Module 07: Streaming and push notifications
> After this module you can read sse frames.

**Time:** ~90 min · **Level:** Beginner · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module 07
**Spec sections:** [Specification](https://a2a-protocol.org/v1.0.1/specification/) · [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path](../../LEARNING_PATH.md). New terms appear in [the glossary](../../docs/GLOSSARY.md).

## Learning objectives

- Read SSE frames
- Assemble artifact chunks
- Verify a push delivery

## The big idea

Server-Sent Events (SSE) keep an HTTP response open and separate events with blank lines. A chunk updates one artifact by ID: append means add to existing content, and lastChunk ends that artifact. It does not finish the task. A webhook reverses the connection: the vendor calls your receiver later. Authenticate deliveries and tolerate retries. Reconnecting with SubscribeToTask does not promise replay of every missed event.

**Analogy:** Streaming is watching a progress board; a webhook is a callback when you are away.

Read the [feature companion](../../docs/FEATURE_DEEP_DIVES.md) for field semantics, failure cases and
the connection to the final deployment.

## How it works

```mermaid
sequenceDiagram
    participant L as Learner
    participant C as Maplewood Concierge
    participant V as Vendor boundary
    L->>C: Event brief and approved scope
    C->>V: Discover or request work
    V-->>C: Typed response or progress event
    C-->>L: Deliverable, question, or failure
```

Under the hood: No. Reconnect with SubscribeToTask or inspect GetTask; cancellation is explicit. Compare that behavior with the captured requests and responses below.

## On the wire

Executed by the course authoring tool through the same recording transport as scripts/wiretap.py. Credentials are redacted. Pure local transformations have no HTTP exchanges and an empty exchange file; their result is separate. gRPC captures are explicitly service-boundary protobuf roundtrips, not network packets.

- [stream: exchanges](wire/01_stream.jsonl) and [result](wire/01_stream.result.json).
- [chunks: exchanges](wire/02_chunks.jsonl) and [result](wire/02_chunks.result.json).
- [push: exchanges](wire/03_push.jsonl) and [result](wire/03_push.result.json).

## Key APIs at a glance

| SDK API | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| a2a.types | Protobuf objects | Defines wire-compatible values | Every protocol boundary |
| create_jsonrpc_routes | JSON-RPC binding | Mounts operations | Serving JSON-RPC |
| create_rest_routes | HTTP+JSON binding | Mounts HTTP routes | Serving HTTP+JSON |
| create_client | Client operations | Selects an advertised interface | Calling vendors |
| MessageToDict | ProtoJSON | Converts protobuf into JSON values | Inspecting traffic |

## Walkthrough

### 01: stream

Read SSE frames.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/07_streaming_push/examples/01_stream.py
```

Captured output (generated values vary):

```json
{
  "result_type": "list",
  "complete_result": "wire/01_stream.result.json"
}
```
### 02: chunks

Assemble artifact chunks.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/07_streaming_push/examples/02_chunks.py
```

Captured output (generated values vary):

```json
{
  "result_type": "list",
  "complete_result": "wire/02_chunks.result.json"
}
```
### 03: push

Verify a push delivery.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/07_streaming_push/examples/03_push.py
```

Captured output (generated values vary):

```json
{
  "result_type": "dict",
  "complete_result": "wire/03_push.result.json"
}
```

## Try it in the Inspector and the Control Room

Start the network in another terminal. Run uv run streamlit run control_room/app.py, select a vendor, inspect its card and send a brief. The Inspector is now a standalone binary; use [its official installation guide](https://github.com/a2aproject/a2a-inspector).

## Real-world use case

Maplewood needs quotes for a 40-person offsite. Run uv run python modules/07_streaming_push/use_case/run.py. The result applies this module's first experiment to shared synthetic data. A real team substitutes validated inventory and its identity system while retaining the A2A boundary.

## Common bugs

| Observed behavior | Cause | Fix |
|---|---|---|
| HTTP 401 | Missing vendor credential | Obtain the vendor token outside A2A and send a header |
| Version not supported | Missing or wrong A2A-Version | Select the card interface and send version 1.0 |
| Task remains interrupted | Required input is missing | Preserve IDs and answer the missing-input request |
| Edge-case assertion fails | Happy path was hard-coded | Work through [Fix task](../../gym/tasks/07/07-02_fix/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
| [07-01](../../gym/tasks/07/07-01_build/task.md) | build | medium | Assemble artifact chunks by artifact ID |
| [07-02](../../gym/tasks/07/07-02_fix/task.md) | fix | easy | Repair: assemble artifact chunks by artifact id |
| [07-03](../../gym/tasks/07/07-03_predict/task.md) | predict | easy | Predict the first experiment's observable result |
| [07-04](../../gym/tasks/07/07-04_trace/task.md) | trace | medium | Identify the captured transport boundaries |
| [07-05](../../gym/tasks/07/07-05_conformance/task.md) | conformance | hard | Enforce the contract across edge cases |
| [07-06](../../gym/tasks/07/07-06_design/task.md) | design | hard | Design a partner contract and failure policy |

### Full boundary exercises

- [07-07: Finish Brightline's streamed artifact](../../gym/tasks/07/07-07_chunks/task.md)
- [07-20: Read state transitions from a real stream](../../gym/tasks/07/07-20_stream_status/task.md)
- [07-21: Assemble an AV artifact across chunks](../../gym/tasks/07/07-21_stream_chunks/task.md)
- [07-22: Audit AV chunk termination](../../gym/tasks/07/07-22_stream_flags/task.md)
- [07-23: Keep task identity across all event variants](../../gym/tasks/07/07-23_stream_identity/task.md)
- [07-24: Separate the final data artifact from progress](../../gym/tasks/07/07-24_stream_quote/task.md)
- [07-25: Reconcile streamed chunks with stored state](../../gym/tasks/07/07-25_stream_snapshot/task.md)
- [07-26: Register an approved callback](../../gym/tasks/07/07-26_push_create/task.md)
- [07-27: Retrieve one callback configuration](../../gym/tasks/07/07-27_push_get/task.md)
- [07-28: Inspect all task callback registrations](../../gym/tasks/07/07-28_push_list/task.md)
- [07-29: Remove a callback without canceling work](../../gym/tasks/07/07-29_push_delete/task.md)
- [07-30: Reject a metadata-service callback](../../gym/tasks/07/07-30_push_ssrf/task.md)
- [07-31: Deliver completion through an authenticated outbox](../../gym/tasks/07/07-31_push_delivery/task.md)

These tasks execute actual SDK routes, workflows, cryptographic checks or independent
database connections offline. Each starter must fail and each reference solution must pass.

## Quiz

1. What does the vendor own?
<details><summary>Answer</summary>Its execution, inventory, task IDs, context scope and authorization policy.</details>

2. How would you demonstrate: read sse frames?
<details><summary>Answer</summary>Run example 01 and identify the exact output field or event that proves the result.</details>

3. Does a signed card grant access?
<details><summary>Answer</summary>No. A trusted signature checks integrity and identity; authorization is enforced separately.</details>

4. Why use a scripted model in graded tasks?
<details><summary>Answer</summary>Repeatable decisions isolate protocol behavior and cost no API tokens.</details>

5. What if an artifact asks for credentials?
<details><summary>Answer</summary>Treat it as untrusted data. Never forward user tokens or expand the allow-list.</details>

6. Which edge case should you test?
<details><summary>Answer</summary>Use the negative cases in this module's Fix task; explain why the broken implementation accepts or mishandles them.</details>

## Key takeaways

- Read typed fields instead of inferring behavior from prose.
- Separate transport concerns from business work.
- Predict before running.
- Test successful and rejected inputs.
- Treat every remote peer as a trust boundary.

## Go deeper

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto) · [Official SDK](https://github.com/a2aproject/a2a-python/tree/v1.3.0)

## Next: Module 08

Use [the learning path](../../LEARNING_PATH.md) to continue or choose a capstone.
