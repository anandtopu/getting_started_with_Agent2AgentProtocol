# Module 02: Agent Cards and discovery
> After this module you can validate a card against protobuf.

**Time:** ~90 min · **Level:** Beginner · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module 02
**Spec sections:** [Specification](https://a2a-protocol.org/v1.0.1/specification/) · [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)
**Network and Concierge version 02:** what's new — agent cards and discovery.

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path](../../LEARNING_PATH.md). New terms appear in [the glossary](../../docs/GLOSSARY.md).

## Learning objectives

- Validate a card against protobuf
- Select a supported interface
- Build a local registry

## The big idea

An Agent Card describes identity, ordered interfaces, capabilities, input and output media types, skills and security requirements. Discovery does not establish trust. A registry is a directory of configured locations, not permission to contact every URL it returns. A skill description is untrusted descriptive text, not an instruction to the Concierge.

**Analogy:** Read a vendor's business card, then check that it came from the vendor you trust.

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

- [discover: exchanges](wire/01_discover.jsonl) and [result](wire/01_discover.result.json).
- [validate_card: exchanges](wire/02_validate_card.jsonl) and [result](wire/02_validate_card.result.json).
- [registry: exchanges](wire/03_registry.jsonl) and [result](wire/03_registry.result.json).

## Key APIs at a glance

| SDK API | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| a2a.types | Protobuf objects | Defines wire-compatible values | Every protocol boundary |
| create_jsonrpc_routes | JSON-RPC binding | Mounts operations | Serving JSON-RPC |
| create_rest_routes | HTTP+JSON binding | Mounts HTTP routes | Serving HTTP+JSON |
| create_client | Client operations | Selects an advertised interface | Calling vendors |
| MessageToDict | ProtoJSON | Converts protobuf into JSON values | Inspecting traffic |

## Walkthrough

### 01: discover

Validate a card against protobuf.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/02_agent_cards/examples/01_discover.py
```

Captured output (generated values vary):

```json
{
  "result_type": "dict",
  "complete_result": "wire/01_discover.result.json"
}
```
### 02: validate card

Select a supported interface.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/02_agent_cards/examples/02_validate_card.py
```

Captured output (generated values vary):

```json
{
  "result_type": "dict",
  "complete_result": "wire/02_validate_card.result.json"
}
```
### 03: registry

Build a local registry.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/02_agent_cards/examples/03_registry.py
```

Captured output (generated values vary):

```json
{
  "venues": [
    {
      "url": "http://127.0.0.1:8100/rpc",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    },
    {
      "url": "http://127.0.0.1:8100",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0"
    }
  ]
}
```

## Try it in the Inspector and the Control Room

Start the network in another terminal. Run uv run streamlit run control_room/app.py, select a vendor, inspect its card and send a brief. The Inspector is now a standalone binary; use [its official installation guide](https://github.com/a2aproject/a2a-inspector).

## Real-world use case

Maplewood needs quotes for a 40-person offsite. Run uv run python modules/02_agent_cards/use_case/run.py. The result applies this module's first experiment to shared synthetic data. A real team substitutes validated inventory and its identity system while retaining the A2A boundary.

## Common bugs

| Observed behavior | Cause | Fix |
|---|---|---|
| HTTP 401 | Missing vendor credential | Obtain the vendor token outside A2A and send a header |
| Version not supported | Missing or wrong A2A-Version | Select the card interface and send version 1.0 |
| Task remains interrupted | Required input is missing | Preserve IDs and answer the missing-input request |
| Edge-case assertion fails | Happy path was hard-coded | Work through [Fix task](../../gym/tasks/02/02-02_fix/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
| [02-01](../../gym/tasks/02/02-01_build/task.md) | build | medium | Select a compatible advertised interface |
| [02-02](../../gym/tasks/02/02-02_fix/task.md) | fix | easy | Repair: select a compatible advertised interface |
| [02-03](../../gym/tasks/02/02-03_predict/task.md) | predict | easy | Predict the first experiment's observable result |
| [02-04](../../gym/tasks/02/02-04_trace/task.md) | trace | medium | Identify the captured transport boundaries |
| [02-05](../../gym/tasks/02/02-05_conformance/task.md) | conformance | hard | Enforce the contract across edge cases |
| [02-06](../../gym/tasks/02/02-06_design/task.md) | design | hard | Design a partner contract and failure policy |

## Quiz

1. What does the vendor own?
<details><summary>Answer</summary>Its execution, inventory, task IDs, context scope and authorization policy.</details>

2. How would you demonstrate: validate a card against protobuf?
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

## Next: Module 03

Use [the learning path](../../LEARNING_PATH.md) to continue or choose a capstone.
