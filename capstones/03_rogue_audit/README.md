# Rogue Agent Audit

As an auditor, I can reproduce six rogue-vendor attacks, show that hardened
boundaries reject them, and deliver an evidence-based findings report.
The [filled-in findings report](FINDINGS.md) records impact, outcome and fix.

## Architecture

~~~mermaid
flowchart LR
    U[User] --> C[Coordinator]
    C --> V[Trusted vendor]
    V --> D[Validated deliverable]
    D --> A[Human approval]
~~~

## Acceptance criteria

- Run the six-attack reference: uv run python capstones/03_rogue_audit/solution/run.py.
- Require all_attacks_blocked to be true and retain the six finding IDs as regression evidence.
- Identify the request, task state, trust decision and resulting deliverable.
- Run this project's tests with uv run pytest capstones/03_rogue_audit/tests.
- Explain the verified boundaries and operating assumptions in the security review.

## Starter

Run uv run python capstones/03_rogue_audit/starter/run.py to inspect the input. Extend it to meet the project contract; compare against the reference only after attempting a design.

## Filled-in security review

| Boundary | Verified control | Scope |
|---|---|---|
| Untrusted cards | Signed and allow-listed discovery; forged card regression | Descriptions remain data even after authentication |
| Poisoned artifacts | Schema validation and restricted delegation fields | Authentic senders can still return hostile content |
| SSRF and replay | Public configured egress, no redirects, signed callbacks | Private destinations need an explicit operator policy |
| Credentials and consent | No forwarded user tokens; approval remains required | No automatic real-world spending |

## Rubric

Score contract clarity, correctness, security, failure handling and evidence from 0 to 2 each. Require at least 8/10 and no zero in security. Automated smoke tests do not replace this review.

## Extend it

Connect this project to the [hardened deployment](../../deploy/HARDENED_NETWORK.md), add a new partner contract, and retain both adversarial and golden regression evidence.
