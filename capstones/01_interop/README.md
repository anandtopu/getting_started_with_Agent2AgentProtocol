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
- Explain the verified boundaries and operating assumptions in the security review.

## Starter

Run uv run python capstones/01_interop/starter/run.py to inspect the input. Extend it to meet the project contract; compare against the reference only after attempting a design.

## Filled-in security review

| Boundary | Verified control | Scope |
|---|---|---|
| Cross-language boundary | Native Python-to-TypeScript quotes and three-binding offline comparison | Native network checks run separately from socket-free grading |
| Authentication | Missing credential and task owner negative cases | Use TLS for any non-loopback deployment |
| Data contract | Same inventory and normalized states/artifacts | Generated IDs are deliberately different |
| Effects | Read-only synthetic venue quotes | No charge or purchase endpoint |

## Rubric

Score contract clarity, correctness, security, failure handling and evidence from 0 to 2 each. Require at least 8/10 and no zero in security. Automated smoke tests do not replace this review.

## Extend it

Connect this project to the [hardened deployment](../../deploy/HARDENED_NETWORK.md), add a new partner contract, and retain both adversarial and golden regression evidence.
