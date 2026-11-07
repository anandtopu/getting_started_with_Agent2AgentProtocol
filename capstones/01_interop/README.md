# Interop Challenge

As a planner, I can request the same quote through all three bindings and verify
that changing a vendor's programming language preserves the business contract.

The default reference compares real SDK JSON-RPC and HTTP+JSON handlers with a
protobuf-roundtrip gRPC service. For the native language acceptance test:

~~~console
npm ci
npm run typecheck
uv run python capstones/01_interop/solution/run.py --native
~~~

This additionally starts the official TypeScript SDK vendor and sends actual
authenticated Python requests. The same native check runs on Windows, macOS and
Linux in CI. See the [TypeScript source](../../modules/bonus/B1_typescript/README.md).

## Architecture

~~~mermaid
flowchart LR
    U[User] --> C[Coordinator]
    C --> V[Trusted vendor]
    V --> D[Validated deliverable]
    D --> A[Human approval]
~~~

## Acceptance criteria

- Run the offline reference: uv run python capstones/01_interop/solution/run.py.
- Require equivalent to be true for all three normalized state/quote results.
- Run --native after installing the pinned npm dependencies.
- Identify the request, task state, trust decision and resulting deliverable.
- Run this project's tests with uv run pytest capstones/01_interop/tests.
- State which production properties are not demonstrated by this slice.

## Starter

Run uv run python capstones/01_interop/starter/run.py to inspect the input. Extend it to meet the project contract; compare against the reference only after attempting a design.

## Filled-in security review

| Control | Reference evidence | Limitation |
|---|---|---|
| Synthetic data | Committed fixtures | No real user-data handling tested |
| Credentials outside messages | HTTP headers in shared clients | Local credentials, not identity-provider integration |
| Destination restriction | Explicit configured vendor clients | Production egress policy remains required |
| Approval | Quotes do not spend money | No purchase workflow implemented |
| Failure handling | Typed task outcomes and security rejection | Full recovery and compensation need extension |

## Rubric

Score contract clarity, correctness, security, failure handling and evidence from 0 to 2 each. Require at least 8/10 and no zero in security. Automated smoke tests do not replace this review.

## Extend it

Add persistent task storage, negative contract tests, reconnect behavior, a durable callback outbox and a real deployment. Prove each property with captured traffic and a regression test.
