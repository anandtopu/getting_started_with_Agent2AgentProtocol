**Network and Concierge version 19:** what's new — deployment and scale.

# Module 19: Deployment and scale
> After this module you can persist and reload a task.

**Time:** ~90 min · **Level:** Advanced · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module 19
**Spec sections:** [Specification](https://a2a-protocol.org/v1.0.1/specification/) · [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path](../../LEARNING_PATH.md). New terms appear in [the glossary](../../docs/GLOSSARY.md).

## Learning objectives

- Persist and reload a task
- Explain multi-replica event delivery
- Identify deployment checks

## The big idea

A persistent task store survives process loss; an in-memory event queue does not coordinate multiple replicas. The current SDK offers a database event stream and versioned database store, which must be paired correctly. Proxies need streaming timeouts and buffering disabled. Webhook retry requires a durable outbox for crash recovery. Docker packages the process; it does not automatically provide trust or persistence.

**Analogy:** Keeping a ledger is different from ensuring every office sees new entries immediately.

Read the [feature companion](../../docs/FEATURE_DEEP_DIVES.md) for field semantics, failure cases and
the connection to the final deployment.

## How it works

```mermaid
sequenceDiagram
    ReplicaA->>Database: Atomic task, journal and outbox commit
    ReplicaA-->>Client: Stream disconnects
    Client->>ReplicaB: Subscribe to existing task
    ReplicaB->>Database: Read committed journal
    Dispatcher->>Webhook: Leased signed delivery
    Webhook-->>Dispatcher: Durable acknowledgement
```

Under the hood: Task storage, event distribution and callback delivery are separate responsibilities. The cluster store commits their records together, then independent workers publish or retry them. Compare-and-swap revisions reject stale writers, while lease fencing rejects late acknowledgements from expired dispatchers.

## On the wire

Executed by the course authoring tool through the same recording transport as scripts/wiretap.py. Credentials are redacted. Pure local transformations have no HTTP exchanges and an empty exchange file; their result is separate. gRPC captures are explicitly service-boundary protobuf roundtrips, not network packets.

- [persist: exchanges](wire/01_persist.jsonl) and [result](wire/01_persist.result.json).
- [stream: exchanges](wire/02_stream.jsonl) and [result](wire/02_stream.result.json).
- [push: exchanges](wire/03_push.jsonl) and [result](wire/03_push.result.json).

## Key APIs at a glance

| SDK API or labeled course helper | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| VersionedTaskStore | Cluster storage contract | Coordinates revision-aware task persistence | Run multiple handlers safely |
| common.cluster.ClusterStore (course) | SQL implementation | Commits task, journal and outbox together | Exercise restart and replica recovery |

## Walkthrough

Run uv run python modules/19_deployment/examples/04_durable_delivery.py to reopen
a SQLite outbox and deliver a pending signed notification. The corresponding
tests/test_durable_delivery.py additionally loses the first acknowledgement,
restarts sender and receiver, and proves the retry creates only one inbox record.

> **Predict, then run:** If a receiver saved the event but its HTTP response was
> lost, should the sender invent a new delivery ID? No: keep the ID so the durable
> inbox can recognize a retry. Authenticate every retry before deduplicating it.

This lab uses one dispatcher and a transactional inbox. It does not make SDK
task persistence and outbox insertion one atomic transaction; closing that gap
requires a shared transaction boundary or reconciliation process. Production
workers also need leases, retention policies and dead-letter operations.

### 01: persist

Persist and reload a task.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/19_deployment/examples/01_persist.py
```

Captured output (generated values vary):

```json
{
  "status": {
    "state": "TASK_STATE_COMPLETED"
  }
}
```
### 02: stream

Explain multi-replica event delivery.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/19_deployment/examples/02_stream.py
```

Captured output (generated values vary):

```json
{
  "result_type": "list",
  "complete_result": "wire/02_stream.result.json"
}
```
### 03: push

Identify deployment checks.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/19_deployment/examples/03_push.py
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

Maplewood stores a paused vendor task, recreates its handler and retrieves the preserved work after restart.

Run:

```console
uv run python modules/19_deployment/use_case/run.py
```

Selected observed fields (see [the complete captured result](wire/01_persist.result.json) for the full output):

```json
{
  "state": "TASK_STATE_COMPLETED"
}
```

A real deployment retains this boundary while substituting its own approved inventory, identity provider and operating policy.

## Common bugs

| Observed behavior | Cause | Fix and related practice |
|---|---|---|
| Task vanishes after restart | Only in-memory storage used | Persist the snapshot and owner scope; [practice 19-40](../../gym/tasks/19/19-40_persistence_reload/task.md) |
| Second replica misses streamed events | Process-local queue used | Pair the task store with a shared journal; [practice 19-42](../../gym/tasks/19/19-42_persistence_replay/task.md) |
| Committed work never notifies | Outbox written in another transaction | Commit task, event and outbox atomically; [practice 19-45](../../gym/tasks/19/19-45_persistence_atomic/task.md) |
| Expired worker marks delivery complete | Lease token not checked | Fence acknowledgement against the current claim; [practice 19-43](../../gym/tasks/19/19-43_persistence_lease/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
| [19-01](../../gym/tasks/19/19-01_build/task.md) | build | medium | Bound webhook retry attempts |
| [19-02](../../gym/tasks/19/19-02_fix/task.md) | fix | easy | Repair: bound webhook retry attempts |
| [19-03](../../gym/tasks/19/19-03_predict/task.md) | predict | easy | Predict the first experiment's observable result |
| [19-04](../../gym/tasks/19/19-04_trace/task.md) | trace | medium | Identify the captured transport boundaries |
| [19-05](../../gym/tasks/19/19-05_conformance/task.md) | conformance | hard | Enforce the contract across edge cases |
| [19-06](../../gym/tasks/19/19-06_design/task.md) | design | hard | Design a partner contract and failure policy |

### Full boundary exercises

- [19-40: Load a task through another replica](../../gym/tasks/19/19-40_persistence_reload/task.md)
- [19-41: Reject a stale task writer](../../gym/tasks/19/19-41_persistence_stale/task.md)
- [19-42: Recover an event before publication](../../gym/tasks/19/19-42_persistence_replay/task.md)
- [19-43: Fence an expired delivery worker](../../gym/tasks/19/19-43_persistence_lease/task.md)
- [19-44: Share a request budget across replicas](../../gym/tasks/19/19-44_persistence_budget/task.md)
- [19-45: Inspect the atomic event and outbox commit](../../gym/tasks/19/19-45_persistence_atomic/task.md)

These tasks execute actual SDK routes, workflows, cryptographic checks or independent
database connections offline. Each starter must fail and each reference solution must pass.

## Quiz

1. Does a SQL task store alone make SSE work across replicas?
<details><summary>Answer</summary>No. Replicas also need a shared event stream or journal.</details>

2. Why commit the outbox with the task snapshot?
<details><summary>Answer</summary>A crash must not leave committed work without its notification record.</details>

3. What prevents stale task writers from overwriting newer work?
<details><summary>Answer</summary>A compare-and-swap revision check in the database transaction.</details>

4. Why fence dispatcher leases?
<details><summary>Answer</summary>An expired worker must not acknowledge another worker's newer claim.</details>

5. Why disable proxy buffering for SSE?
<details><summary>Answer</summary>Otherwise progress can arrive only after the response finishes.</details>

6. What operational work remains beyond a green Compose test?
<details><summary>Answer</summary>Certificate renewal, backups, retention, monitoring and capacity planning.</details>

## Key takeaways

- No. Replicas also need a shared event stream or journal.
- A crash must not leave committed work without its notification record.
- A compare-and-swap revision check in the database transaction.
- An expired worker must not acknowledge another worker's newer claim.
- Otherwise progress can arrive only after the response finishes.

## Go deeper

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto) · [Official SDK](https://github.com/a2aproject/a2a-python/tree/v1.3.0)

## Next: Module 20

Use [the learning path](../../LEARNING_PATH.md) to continue or choose a capstone.

## Connected integration lab

Continue with [the tested integration walkthrough](../../docs/INTEGRATION_LABS.md), including actual commands, expected behavior, security boundaries and current limitations.
