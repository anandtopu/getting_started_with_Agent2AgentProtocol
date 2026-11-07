# Design Your Own Network

As a recruiting-network designer, I can coordinate three real in-process A2A agents: a recruiter, a candidate scheduling assistant and a consent-gated background-check fixture. All data is synthetic. The reference never makes an employment eligibility decision.

The recruiter sends only proposed UTC slots to the candidate and only consent to
the background fixture. Missing consent pauses both the background task and the
recruiter task. The next turn resumes their original task IDs while preserving
the completed scheduling result. All final results require human review.

The implementation is [common/hiring.py](../../common/hiring.py). Tests inspect
actual requests for minimal disclosure and verify the complete consent continuation.

## Architecture

~~~mermaid
flowchart LR
    U[User] --> C[Coordinator]
    C --> V[Trusted vendor]
    V --> D[Validated deliverable]
    D --> A[Human approval]
~~~

## Acceptance criteria

- Run the reference slice: uv run python capstones/05_design_network/solution/run.py.
- Identify the request, task state, trust decision and resulting deliverable.
- Run this project's tests with uv run pytest capstones/05_design_network/tests.
- State which production properties are not demonstrated by this slice.

## Starter

Run uv run python capstones/05_design_network/starter/run.py to inspect the input. Extend it to meet the project contract; compare against the reference only after attempting a design.

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
