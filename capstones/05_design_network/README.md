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
- Explain the verified boundaries and operating assumptions in the security review.

## Starter

Run uv run python capstones/05_design_network/starter/run.py to inspect the input. Extend it to meet the project contract; compare against the reference only after attempting a design.

## Filled-in security review

| Boundary | Verified control | Scope |
|---|---|---|
| Candidate consent | Background check pauses until explicit consent | Synthetic fixture consent is not a real legal workflow |
| Minimum disclosure | Only necessary availability/consent fields delegated | No real candidate data is present |
| Ownership | Each agent owns its own task/context mapping | Cross-organization authorization must be provisioned separately |
| Effects | Scheduling proposals and synthetic check result | No real hiring decision is made |

## Rubric

Score contract clarity, correctness, security, failure handling and evidence from 0 to 2 each. Require at least 8/10 and no zero in security. Automated smoke tests do not replace this review.

## Extend it

Connect this project to the [hardened deployment](../../deploy/HARDENED_NETWORK.md), add a new partner contract, and retain both adversarial and golden regression evidence.
