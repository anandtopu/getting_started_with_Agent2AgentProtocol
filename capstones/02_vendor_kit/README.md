# Vendor Agent Kit

As a vendor, I can publish a signed card, authenticate callers, pause for dietary
counts, resume over a stream, persist tasks, and recover signed callbacks after a
restart. As a receiver, I can accept a retried delivery without repeating its effect.

The [reference bundle](../../common/vendor_kit.py) combines the official SDK with
ClusterStore, a database callback registry, an atomic task/event/outbox transaction,
leased dispatch and a durable verified inbox. It accepts SQLite or PostgreSQL URLs,
operator keys and an exact destination allow-list.

~~~mermaid
sequenceDiagram
    participant C as Concierge
    participant V as Vendor kit
    participant D as SQL task and outbox
    participant W as Recovery dispatcher
    participant R as Verified inbox
    C->>V: Authenticated message and callback config
    V->>D: Commit task, event and delivery together
    V-->>C: input-required or streamed quote
    W->>D: Claim delivery lease
    W->>R: Signed body, timestamp and delivery ID
    R-->>W: Acknowledge durable acceptance or duplicate
    W->>D: Acknowledge current lease
~~~

## Build and run

~~~console
uv run python capstones/02_vendor_kit/starter/run.py
uv run python capstones/02_vendor_kit/solution/run.py
uv run pytest capstones/02_vendor_kit/tests tests/test_cluster.py tests/test_durable_delivery.py
uv run python scripts/check_webhook_lab.py
~~~

To watch callbacks, start `uv run python scripts/webhook_lab.py` and then
`uv run streamlit run control_room/app.py` in another terminal. The local lab uses
fresh ignored credentials, fixed loopback ports and persistent SQLite files.

## Acceptance criteria

- Verify the card with a separately trusted public key; reject unsigned requests.
- Preserve task/context IDs through input-required and streaming continuation.
- Return a structured quote artifact, with no charge or implicit purchase.
- Commit the task, event and outbox atomically; a forced failure leaves none written.
- Recover eligible callbacks after restart without requiring another user request.
- Reject forged callbacks and reused delivery IDs with different bodies; deduplicate
  authenticated retries after a lost acknowledgement.
- Fence expired dispatcher leases, bound retries, and surface dead deliveries.
- Run all three binding contracts and review the [official TCK result](../../docs/TCK_REPORT.md).

## Filled-in security review

| Control | Evidence | Operating responsibility |
|---|---|---|
| Authentication and owner isolation | SDK routes plus BearerGate; cluster owner tests | Provision/revoke vendor identities |
| Signed identity | Separate signing and trusted verification keys | Preserve wrapping key; rotate/revoke keys |
| Callback trust | Exact URL allow-list and HMAC verification before acceptance | Configure private destinations; never accept arbitrary URLs |
| Recovery | Atomic SQL outbox, leases, bounded backoff, durable inbox | Monitor dead deliveries and apply retention |
| Encrypted deployment | Hardened Compose, CA validation and mTLS tests | Renew certificates and protect secrets |
| Effects | Quote-only contract and explicit no-charge holds | Add an independently reviewed approval workflow before purchases |

## Rubric

Score protocol lifecycle, durable recovery, authorization, verified delivery and
operational evidence from 0–2 each. Require 8/10 and no zero for authorization or
recovery. Show the injected failure and recovery evidence, not only a happy-path quote.

## Extend it

Add a receiver-specific OAuth scheme, a custom dead-letter dashboard or a managed
certificate issuer. Preserve the same callback authentication and idempotency tests.
Use the [deployment runbook](../../deploy/HARDENED_NETWORK.md) for backup and rollout.
