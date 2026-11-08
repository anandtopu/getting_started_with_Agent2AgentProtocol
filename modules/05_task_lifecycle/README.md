**Network and Concierge version 05:** what's new — the task lifecycle in depth.

# Module 05: The task lifecycle in depth
> After this module you can resume a paused catering task.

**Time:** ~90 min · **Level:** Beginner · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module 05
**Spec sections:** [Specification](https://a2a-protocol.org/v1.0.1/specification/) · [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path](../../LEARNING_PATH.md). New terms appear in [the glossary](../../docs/GLOSSARY.md).

## Learning objectives

- Resume a paused catering task
- Cancel unfinished work
- Distinguish interrupted from terminal states

## The big idea

Submitted and working are active states. Input-required and auth-required interrupt work without ending the task. Completed, failed, canceled and rejected are terminal: create a new task for new work after these states. Keep task and context IDs when answering a request for missing input. The wire uses uppercase protobuf enum names. TASK_STATE_UNSPECIFIED is a sentinel, not a useful success state.

**Analogy:** A work order awaiting dietary counts stays open; a completed quote is filed.

Read the [feature companion](../../docs/FEATURE_DEEP_DIVES.md) for field semantics, failure cases and
the connection to the final deployment.

## How it works

```mermaid
sequenceDiagram
    Concierge->>Saffron: SendMessage without dietary counts
    Saffron-->>Concierge: Task T, input-required
    Concierge->>Saffron: Dietary counts with task T and same context
    Saffron-->>Concierge: Quote artifact and completed
```

Under the hood: Paused work retains its brief and task identity. Terminal tasks cannot be resumed; new work needs a new task. Cancellation is a protocol state change for unfinished work, while undoing a completed business reservation needs a separate release operation.

## On the wire

Executed by the course authoring tool through the same recording transport as scripts/wiretap.py. Credentials are redacted. Pure local transformations have no HTTP exchanges and an empty exchange file; their result is separate. gRPC captures are explicitly service-boundary protobuf roundtrips, not network packets.

- [pause: exchanges](wire/01_pause.jsonl) and [result](wire/01_pause.result.json).
- [resume: exchanges](wire/02_resume.jsonl) and [result](wire/02_resume.result.json).
- [cancel: exchanges](wire/03_cancel.jsonl) and [result](wire/03_cancel.result.json).

## Key APIs at a glance

| SDK API or labeled course helper | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| TaskState | Lifecycle state | Distinguishes active, interrupted and terminal work | Choose a continuation action |
| TaskStatusUpdateEvent | Status event | Updates a task's state and message | Pause, complete or cancel work |

## Walkthrough

### 01: pause

Resume a paused catering task.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/05_task_lifecycle/examples/01_pause.py
```

Captured output (generated values vary):

```json
{
  "status": {
    "state": "TASK_STATE_INPUT_REQUIRED",
    "message": {
      "role": "ROLE_AGENT",
      "parts": [
        {
          "text": "How many guests need each dietary option?"
        }
      ]
    }
  },
  "history": [
    {
      "role": "ROLE_USER",
      "parts": [
        {
          "data": {
            "guests": 40.0
          },
          "mediaType": "application/json"
        }
      ]
    },
    {
      "role": "ROLE_AGENT",
      "parts": [
        {
          "text": "catering: checking the brief"
        }
      ]
    }
  ],
  "metadata": {
    "brief": {
      "guests": 40.0
    }
  }
}
```
### 02: resume

Cancel unfinished work.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/05_task_lifecycle/examples/02_resume.py
```

Captured output (generated values vary):

```json
{
  "result_type": "dict",
  "complete_result": "wire/02_resume.result.json"
}
```
### 03: cancel

Distinguish interrupted from terminal states.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/05_task_lifecycle/examples/03_cancel.py
```

Captured output (generated values vary):

```json
{
  "status": {
    "state": "TASK_STATE_CANCELED",
    "message": {
      "role": "ROLE_AGENT",
      "parts": [
        {
          "text": "Work canceled. No booking was made."
        }
      ]
    }
  },
  "history": [
    {
      "role": "ROLE_USER",
      "parts": [
        {
          "data": {
            "guests": 40.0
          },
          "mediaType": "application/json"
        }
      ]
    },
    {
      "role": "ROLE_AGENT",
      "parts": [
        {
          "text": "catering: checking the brief"
        }
      ]
    },
    {
      "role": "ROLE_AGENT",
      "parts": [
        {
          "text": "How many guests need each dietary option?"
        }
      ]
    }
  ],
  "metadata": {
    "brief": {
      "guests": 40.0
    }
  }
}
```

## Try it in the Inspector and the Control Room

Start the network in another terminal. Run uv run streamlit run control_room/app.py, select a vendor, inspect its card and send a brief. The Inspector is now a standalone binary; use [its official installation guide](https://github.com/a2aproject/a2a-inspector).

## Real-world use case

Saffron receives an incomplete offsite brief and asks Maplewood for dietary counts rather than guessing a menu.

Run:

```console
uv run python modules/05_task_lifecycle/use_case/run.py
```

Selected observed fields (see [the complete captured result](wire/01_pause.result.json) for the full output):

```json
{
  "state": "TASK_STATE_INPUT_REQUIRED"
}
```

A real deployment retains this boundary while substituting its own approved inventory, identity provider and operating policy.

## Common bugs

| Observed behavior | Cause | Fix and related practice |
|---|---|---|
| Second catering task appears | Follow-up omitted taskId | Keep the returned task and context IDs; [practice 05-02](../../gym/tasks/05/05-02_fix/task.md) |
| Task cannot be canceled | It already reached a terminal state | Use a new business operation where needed; [practice 05-21](../../gym/tasks/05/05-21_lifecycle_cancel/task.md) |
| Continuation loses guest count | Paused brief was discarded | Merge new fields into the stored brief; [practice 05-20](../../gym/tasks/05/05-20_lifecycle_resume/task.md) |
| Listing exposes another caller's work | Owner filtering bypassed | Use the authenticated task store context; [practice 05-23](../../gym/tasks/05/05-23_lifecycle_list/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
| [05-01](../../gym/tasks/05/05-01_build/task.md) | build | medium | Distinguish terminal from interrupted states |
| [05-02](../../gym/tasks/05/05-02_fix/task.md) | fix | easy | Repair: distinguish terminal from interrupted states |
| [05-03](../../gym/tasks/05/05-03_predict/task.md) | predict | easy | Predict the first experiment's observable result |
| [05-04](../../gym/tasks/05/05-04_trace/task.md) | trace | medium | Identify the captured transport boundaries |
| [05-05](../../gym/tasks/05/05-05_conformance/task.md) | conformance | hard | Enforce the contract across edge cases |
| [05-06](../../gym/tasks/05/05-06_design/task.md) | design | hard | Design a partner contract and failure policy |

### Full boundary exercises

- [05-07: Resume Saffron without losing its work order](../../gym/tasks/05/05-07_resume/task.md)
- [05-20: Continue Saffron's stored work order](../../gym/tasks/05/05-20_lifecycle_resume/task.md)
- [05-21: Cancel paused catering work](../../gym/tasks/05/05-21_lifecycle_cancel/task.md)
- [05-22: Request bounded task history](../../gym/tasks/05/05-22_lifecycle_history/task.md)
- [05-23: Page through owner-scoped tasks](../../gym/tasks/05/05-23_lifecycle_list/task.md)
- [05-24: Pause for out-of-band authorization](../../gym/tasks/05/05-24_lifecycle_auth/task.md)
- [05-25: Reject an impossible catering request](../../gym/tasks/05/05-25_lifecycle_rejected/task.md)

These tasks execute actual SDK routes, workflows, cryptographic checks or independent
database connections offline. Each starter must fail and each reference solution must pass.

## Quiz

1. Which states are paused?
<details><summary>Answer</summary>INPUT_REQUIRED and AUTH_REQUIRED.</details>

2. Which states are terminal?
<details><summary>Answer</summary>COMPLETED, FAILED, CANCELED and REJECTED.</details>

3. Which IDs continue a paused conversation?
<details><summary>Answer</summary>The remote task ID and its context ID.</details>

4. Does contextId alone resume a task?
<details><summary>Answer</summary>No. Supply taskId for the particular interrupted work.</details>

5. Can CancelTask undo a completed hotel hold?
<details><summary>Answer</summary>No. Use an explicit compensating release skill.</details>

6. Do repeated message IDs guarantee exactly-once work?
<details><summary>Answer</summary>No. Application idempotency must protect business effects.</details>

## Key takeaways

- INPUT_REQUIRED and AUTH_REQUIRED.
- COMPLETED, FAILED, CANCELED and REJECTED.
- The remote task ID and its context ID.
- No. Supply taskId for the particular interrupted work.
- No. Use an explicit compensating release skill.

## Go deeper

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto) · [Official SDK](https://github.com/a2aproject/a2a-python/tree/v1.3.0)

## Next: Module 06

Use [the learning path](../../LEARNING_PATH.md) to continue or choose a capstone.
