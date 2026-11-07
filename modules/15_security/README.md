# Module 15: Security threats and defenses
> After this module you can reject unsafe destinations.

**Time:** ~90 min · **Level:** Advanced · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module 15
**Spec sections:** [Specification](https://a2a-protocol.org/v1.0.1/specification/) · [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)
**Network and Concierge version 15:** what's new — security threats and defenses.

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path](../../LEARNING_PATH.md). New terms appear in [the glossary](../../docs/GLOSSARY.md).

## Learning objectives

- Reject unsafe destinations
- Prevent credential delegation
- Explain layered defenses

## The big idea

Treat cards, messages and artifacts as untrusted inputs. Prompt injection attempts to turn those inputs into higher-priority instructions. Allow-list destinations, validate outputs, keep tokens scoped, and require human approval before spending. Private-address filtering alone does not prevent DNS rebinding; use a controlled egress path or inline files. Limit bytes, duration, concurrency and tool steps.

**Analogy:** A forged purchase order cannot override the company's approval policy.

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

Under the hood, protobuf objects become JSON or binary bytes at the boundary. Route handlers enforce operation contracts; the executor performs business work. Compare the captured result with your prediction.

## On the wire

Executed by the course authoring tool through the same recording transport as scripts/wiretap.py. Credentials are redacted. Pure local transformations have no HTTP exchanges and an empty exchange file; their result is separate. gRPC captures are explicitly service-boundary protobuf roundtrips, not network packets.

- [ssrf: exchanges](wire/01_ssrf.jsonl) and [result](wire/01_ssrf.result.json).
- [forgery: exchanges](wire/02_forgery.jsonl) and [result](wire/02_forgery.result.json).
- [minimize: exchanges](wire/03_minimize.jsonl) and [result](wire/03_minimize.result.json).

## Key APIs at a glance

| SDK API | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| a2a.types | Protobuf objects | Defines wire-compatible values | Every protocol boundary |
| create_jsonrpc_routes | JSON-RPC binding | Mounts operations | Serving JSON-RPC |
| create_rest_routes | HTTP+JSON binding | Mounts HTTP routes | Serving HTTP+JSON |
| create_client | Client operations | Selects an advertised interface | Calling vendors |
| MessageToDict | ProtoJSON | Converts protobuf into JSON values | Inspecting traffic |

## Walkthrough

### 01: ssrf

Reject unsafe destinations.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/15_security/examples/01_ssrf.py
```

Captured output (generated values vary):

```json
{
  "blocked": [
    "https://127.0.0.1/private",
    "https://169.254.169.254/latest"
  ]
}
```
### 02: forgery

Prevent credential delegation.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/15_security/examples/02_forgery.py
```

Captured output (generated values vary):

```json
{
  "rejected": true,
  "reason": "Card signature did not verify"
}
```
### 03: minimize

Explain layered defenses.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/15_security/examples/03_minimize.py
```

Captured output (generated values vary):

```json
{
  "result_type": "dict",
  "complete_result": "wire/03_minimize.result.json"
}
```

## Try it in the Inspector and the Control Room

Start the network in another terminal. Run uv run streamlit run control_room/app.py, select a vendor, inspect its card and send a brief. The Inspector is now a standalone binary; use [its official installation guide](https://github.com/a2aproject/a2a-inspector).

## Real-world use case

Maplewood needs quotes for a 40-person offsite. Run uv run python modules/15_security/use_case/run.py. The result applies this module's first experiment to shared synthetic data. A real team substitutes validated inventory and its identity system while retaining the A2A boundary.

## Common bugs

| Observed behavior | Cause | Fix |
|---|---|---|
| HTTP 401 | Missing vendor credential | Obtain the vendor token outside A2A and send a header |
| Version not supported | Missing or wrong A2A-Version | Select the card interface and send version 1.0 |
| Task remains interrupted | Required input is missing | Preserve IDs and answer the missing-input request |
| Edge-case assertion fails | Happy path was hard-coded | Work through [Fix task](../../gym/tasks/15/15-02_fix/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
| [15-01](../../gym/tasks/15/15-01_build/task.md) | build | medium | Reject private and reserved IP addresses |
| [15-02](../../gym/tasks/15/15-02_fix/task.md) | fix | easy | Repair: reject private and reserved ip addresses |
| [15-03](../../gym/tasks/15/15-03_predict/task.md) | predict | easy | Predict the first experiment's observable result |
| [15-04](../../gym/tasks/15/15-04_trace/task.md) | trace | medium | Identify the captured transport boundaries |
| [15-05](../../gym/tasks/15/15-05_conformance/task.md) | conformance | hard | Enforce the contract across edge cases |
| [15-06](../../gym/tasks/15/15-06_design/task.md) | design | hard | Design a partner contract and failure policy |

## Quiz

1. What does the vendor own?
<details><summary>Answer</summary>Its execution, inventory, task IDs, context scope and authorization policy.</details>

2. How would you demonstrate: reject unsafe destinations?
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

## Next: Module 16

Use [the learning path](../../LEARNING_PATH.md) to continue or choose a capstone.
