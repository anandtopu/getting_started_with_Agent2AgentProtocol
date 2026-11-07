# Vendor Agent Kit

As a vendor, I can expose a signed card, require authentication, persist tasks,
pause for dietary counts, continue over a stream and deliver verified push events.
The [integrated implementation](../../common/vendor_kit.py) composes all of these
features and accepts a SQLite or PostgreSQL URL and operator-provisioned keys.
Callback registrations and tasks use database stores. The immediate callback
receiver still keeps replay history in memory; the separate
[durable-delivery lab](../../modules/19_deployment/examples/04_durable_delivery.py)
demonstrates restart-safe outbox/inbox behavior. Combining task changes and outbox
insertion in one transaction remains production work.

## Architecture

~~~mermaid
flowchart LR
    U[User] --> C[Coordinator]
    C --> V[Trusted vendor]
    V --> D[Validated deliverable]
    D --> A[Human approval]
~~~

## Acceptance criteria

- Run the reference slice: uv run python capstones/02_vendor_kit/solution/run.py.
- Identify the request, task state, trust decision and resulting deliverable.
- Run this project's tests with uv run pytest capstones/02_vendor_kit/tests.
- State which production properties are not demonstrated by this slice.

## Starter

Run uv run python capstones/02_vendor_kit/starter/run.py to inspect the input. Extend it to meet the project contract; compare against the reference only after attempting a design.

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

Add migrations, backup/restore checks, reconnect behavior, an atomic task/outbox
transaction and a public TLS deployment. Prove each property with captured traffic
and a regression test.
