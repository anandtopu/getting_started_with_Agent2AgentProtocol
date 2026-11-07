# Maplewood Concierge

As a planner, I can ask five vendors for quotes, retain their task/context mapping and see a combined cost that still requires approval.

The offline reference uses a scripted model, a real LangGraph catering workflow
with an internal MCP kitchen, and five A2A vendor boundaries. It pauses for dietary
counts, then resumes the original catering task without repeating completed quotes.
The model is consulted only once, so continuation cannot silently expand delegation.

## Run the complete local integration

~~~console
uv run python scripts/setup_frameworks.py
uv run python scripts/check_network.py --module 11 --frameworks
uv run pytest tests/test_golden.py tests/test_observability.py tests/test_recovery.py
~~~

This installs the isolated framework environments and starts a real six-process
network with ADK, Strands, Pydantic AI, CrewAI and BeeAI vendors. The Concierge
verifies their signed cards, uses a separate credential for each vendor, delegates
to Inkwell through gRPC and closes the processes after the check.
For optional model-driven planning use [the live-model guide](../../docs/LIVE_MODELS.md).
For PostgreSQL recovery and Jaeger export use [the container lab](../../deploy/README.md).
The container image currently uses deterministic Python vendors; isolated framework
workers are a separate local-network mode.

## Architecture

~~~mermaid
flowchart LR
    U[User] --> C[Coordinator]
    C --> V[Trusted vendor]
    V --> D[Validated deliverable]
    D --> A[Human approval]
~~~

## Acceptance criteria

- Run the offline reference: uv run python capstones/04_concierge/solution/run.py.
- Verify the catering task pauses and resumes with identical task/context IDs.
- Verify completed vendor tasks are reused and approval_required remains true.
- Identify the request, task state, trust decision and resulting deliverable.
- Run this project's tests with uv run pytest capstones/04_concierge/tests.
- State which production properties are not demonstrated by this slice.

## Starter

Run uv run python capstones/04_concierge/starter/run.py to inspect the input. Extend it to meet the project contract; compare against the reference only after attempting a design.

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
