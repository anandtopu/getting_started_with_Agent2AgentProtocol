**Network and Concierge version 09:** what's new — putting an llm behind a server.

# Module 09: Putting an LLM behind a server
> After this module you can replace model output with a script.

**Time:** ~90 min · **Level:** Intermediate · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module 09
**Spec sections:** [Specification](https://a2a-protocol.org/v1.0.1/specification/) · [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path](../../LEARNING_PATH.md). New terms appear in [the glossary](../../docs/GLOSSARY.md).

## Learning objectives

- Replace model output with a script
- Validate tool choices
- Bound model work

## The big idea

A language model predicts output from context; it is not the protocol and should not calculate binding prices. A tool call asks application code to run a named function with validated arguments. The course first scripts model decisions, making failures repeatable and free. Provider configuration lives in one helper. Every tool loop has a step limit and every business action has validation.

**Analogy:** A junior estimator suggests an action; the office's checked procedures decide what may happen.

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

Under the hood: No. Emit safe progress and the validated deliverable, not internal reasoning or partial tool arguments. Compare that behavior with the captured requests and responses below.

## On the wire

Executed by the course authoring tool through the same recording transport as scripts/wiretap.py. Credentials are redacted. Pure local transformations have no HTTP exchanges and an empty exchange file; their result is separate. gRPC captures are explicitly service-boundary protobuf roundtrips, not network packets.

- [fake_llm: exchanges](wire/01_fake_llm.jsonl) and [result](wire/01_fake_llm.result.json).
- [tool_call: exchanges](wire/02_tool_call.jsonl) and [result](wire/02_tool_call.result.json).
- [tool_budget: exchanges](wire/03_tool_budget.jsonl) and [result](wire/03_tool_budget.result.json).

## Key APIs at a glance

| SDK API | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| a2a.types | Protobuf objects | Defines wire-compatible values | Every protocol boundary |
| create_jsonrpc_routes | JSON-RPC binding | Mounts operations | Serving JSON-RPC |
| create_rest_routes | HTTP+JSON binding | Mounts HTTP routes | Serving HTTP+JSON |
| create_client | Client operations | Selects an advertised interface | Calling vendors |
| MessageToDict | ProtoJSON | Converts protobuf into JSON values | Inspecting traffic |

## Walkthrough

### 01: fake llm

Replace model output with a script.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/09_llm_server/examples/01_fake_llm.py
```

Captured output (generated values vary):

```json
{
  "state": "TASK_STATE_COMPLETED",
  "quote": {
    "vendor": "catering",
    "selection": "garden",
    "currency": "USD",
    "total_cents": 96000,
    "guests": 40,
    "approved": false
  }
}
```
### 02: tool call

Validate tool choices.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/09_llm_server/examples/02_tool_call.py
```

Captured output (generated values vary):

```json
{
  "state": "TASK_STATE_COMPLETED",
  "quote": {
    "vendor": "catering",
    "selection": "garden",
    "currency": "USD",
    "total_cents": 96000,
    "guests": 40,
    "approved": false
  }
}
```
### 03: tool budget

Bound model work.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/09_llm_server/examples/03_tool_budget.py
```

Captured output (generated values vary):

```json
{
  "rejected": "Model exceeded the three-step tool budget."
}
```

## Try it in the Inspector and the Control Room

Start the network in another terminal. Run uv run streamlit run control_room/app.py, select a vendor, inspect its card and send a brief. The Inspector is now a standalone binary; use [its official installation guide](https://github.com/a2aproject/a2a-inspector).

## Real-world use case

Maplewood needs quotes for a 40-person offsite. Run uv run python modules/09_llm_server/use_case/run.py. The result applies this module's first experiment to shared synthetic data. A real team substitutes validated inventory and its identity system while retaining the A2A boundary.

## Common bugs

| Observed behavior | Cause | Fix |
|---|---|---|
| HTTP 401 | Missing vendor credential | Obtain the vendor token outside A2A and send a header |
| Version not supported | Missing or wrong A2A-Version | Select the card interface and send version 1.0 |
| Task remains interrupted | Required input is missing | Preserve IDs and answer the missing-input request |
| Edge-case assertion fails | Happy path was hard-coded | Work through [Fix task](../../gym/tasks/09/09-02_fix/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
| [09-01](../../gym/tasks/09/09-01_build/task.md) | build | medium | Validate model-selected tool names |
| [09-02](../../gym/tasks/09/09-02_fix/task.md) | fix | easy | Repair: validate model-selected tool names |
| [09-03](../../gym/tasks/09/09-03_predict/task.md) | predict | easy | Predict the first experiment's observable result |
| [09-04](../../gym/tasks/09/09-04_trace/task.md) | trace | medium | Identify the captured transport boundaries |
| [09-05](../../gym/tasks/09/09-05_conformance/task.md) | conformance | hard | Enforce the contract across edge cases |
| [09-06](../../gym/tasks/09/09-06_design/task.md) | design | hard | Design a partner contract and failure policy |

### Full boundary exercises

- [09-40: Validate native tool frames: ollama](../../gym/tasks/09/09-40_native_model_ollama/task.md)
- [09-41: Validate native tool frames: openai](../../gym/tasks/09/09-41_native_model_openai/task.md)
- [09-42: Validate native tool frames: anthropic](../../gym/tasks/09/09-42_native_model_anthropic/task.md)
- [09-43: Validate native tool frames: gemini](../../gym/tasks/09/09-43_native_model_gemini/task.md)
- [09-44: Validate native tool frames: truncated](../../gym/tasks/09/09-44_native_model_truncated/task.md)
- [09-45: Validate native tool frames: unsafe](../../gym/tasks/09/09-45_native_model_unsafe/task.md)

These tasks execute actual SDK routes, workflows, cryptographic checks or independent
database connections offline. Each starter must fail and each reference solution must pass.

## Quiz

1. What does the vendor own?
<details><summary>Answer</summary>Its execution, inventory, task IDs, context scope and authorization policy.</details>

2. How would you demonstrate: replace model output with a script?
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

## Next: Module 10

Use [the learning path](../../LEARNING_PATH.md) to continue or choose a capstone.
