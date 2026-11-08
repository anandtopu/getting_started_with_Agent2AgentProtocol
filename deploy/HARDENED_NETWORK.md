# Encrypted, mixed-framework Maplewood network

The final network runs five vendors behind the official A2A 1.0 boundary and a
Concierge that discovers signed cards, chooses trusted skills, and aggregates quotes.
The same lifecycle adapter supplies pause/resume, rejection, cancellation, files and
AV artifact chunks regardless of the vendor's internal framework.

| Vendor | Internal runtime | Authentication |
|---|---|---|
| Granite Hall | Google ADK | HTTP bearer token |
| Saffron Table | Strands | X-API-Key header |
| Brightline AV | Pydantic AI | OAuth client credentials, AV audience and quote scope |
| Northstar | CrewAI | OIDC issuer/JWKS, travel audience and quote scope |
| Inkwell | BeeAI | gRPC mutual TLS, authorized client certificate identity |
| Concierge | Python orchestration; optional model | Its own bearer token |

LangGraph and Microsoft Agent Framework have additional verified adapters in
[the runtime matrix](../integrations/README.md). Incompatible framework-native
legacy adapters are isolated from the official v1 boundary.

## Start and check

Run from the repository root on PowerShell, bash or zsh:

~~~console
uv sync --locked --extra production
uv run python deploy/prepare.py
uv run python deploy/certificates.py
docker compose --env-file deploy/secrets/network.env -f deploy/docker-compose.yml -f deploy/hardened.yml -f deploy/frameworks.yml up --build -d
uv run python scripts/check_hardened.py
~~~

The checker verifies all six signatures over trusted HTTPS, rejects a token issued
for another vendor, makes a five-vendor plan, exercises all twenty golden plans,
and calls Inkwell with a client certificate. GitHub's hardened-frameworks job runs
these commands against real PostgreSQL, Keycloak and framework workers.

Stop with the same Compose options followed by `down`. Volumes retain tasks;
deleting volumes discards the lab database. Ports bind only to loopback. The local
CA is a teaching CA: clients explicitly trust its certificate, validate hostnames,
and require TLS 1.2 or newer. Leaf certificates expire after seven days. Regenerate
them and recreate the containers to rehearse certificate renewal. For a real service,
issue the same server/client identities through your organization's certificate service.

## Keys and identity

The Concierge has separate AV and travel service accounts and never forwards the
user's token. OIDC validation pins issuer, audience, scope, algorithm and operator
JWKS location. Unknown keys trigger bounded refresh; unavailable/expired keys fail
closed. Token acquisition and refresh happen outside A2A message parts.

Card signing keys rotate every five minutes with a ninety-second overlap. A shared,
encrypted SQL key ring keeps independent replicas consistent and survives restart.
The wrapping secret comes from MAPLEWOOD_SIGNING_KEY in the protected deployment
environment; it is absent from the database and must be backed up separately.
The HTTPS vendor location, not a URL embedded in a card, anchors JWKS discovery.
Card caching is thirty seconds. Revocation removes a key immediately from JWKS;
clients fetch JWKS on each discovery verification.

## Failure and recovery contract

ClusterStore commits the SDK task snapshot, revision, event journal and callback
outbox together. Compare-and-swap rejects stale normal writers. Cancellation
atomically supersedes nonterminal work, even when its caller read an older version.
The SDK's SubscribeToTask combines a snapshot and journal cursor; a second replica
can resume delivery after the first connection disappears. A disconnected client
does not imply canceled business work. Reconcile with GetTask after reconnecting.

Dispatchers claim short leases, retry with bounded backoff, and dead-letter after
eight attempts. An expired worker cannot acknowledge a newer worker's delivery.
Delivery is at least once and can be reordered across concurrent dispatchers.
Receivers authenticate every retry, deduplicate durable delivery IDs, and reconcile
the latest task before performing effects. Do not interpret receipt order as a
global business ordering guarantee. The vendor kit runs a recovery loop independently
of new task traffic; restart alone is enough to retry eligible queued notifications.

The SQL rate budget is shared across HTTP and gRPC replicas. Task ownership uses
the validated tenant plus subject, never a tenant supplied in a message. A task ID
is a lookup key, not authorization.

## Runbook

1. Initialize the schema once before admitting traffic from new replicas. With the
   vendor's deployment environment loaded, run `uv run python scripts/init_database.py --vendor venues`
   (substitute each vendor name). `ClusterStore.initialize()`
   and `SharedCardKeys.initialize()` create the pinned course schema. `create_all` is
   not a general schema migration engine: version future DDL changes, test them on
   a restored copy, and roll out readers compatible with both versions first.
2. Back up PostgreSQL with `pg_dump` and preserve the deployment secrets separately.
   Restore into an isolated database with `pg_restore`, start one replica using that
   database URL and the original wrapping key, then run the restart, lease and owner
   checks before switching traffic. SQLite teaching databases must be backed up with
   SQLite's backup API or while all writers are stopped; copying a live main file can
   omit its WAL.
3. After a failed deployment, restore the previous image and configuration. Do not
   drop tables to repair a startup error. Inspect the database version and wrapping
   secret first. Replaying an outbox is safe only with durable receiver deduplication.
4. Monitor failed/expired tasks, queued/dead callbacks, token refresh failures, and
   lease age. Logs omit credentials. Trace attributes include maplewood.task.id,
   maplewood.context.id and maplewood.vendor; these are course conventions.
5. Apply an agreed retention period through owner-authorized store deletion after
   downstream consumers finish. Journal retention bounds the recovery window; do not
   delete a journal still needed by a paused task or delayed subscriber. Purge expired
   rate-budget identities and completed delivery records during planned maintenance.

No purchase endpoint exists. Optional tentative venue/hotel holds are idempotent,
expire after fifteen minutes, and charge nothing. When an acknowledgement is lost,
release_request fences late retries by business request ID. Failed cleanup returns
manual_followup_required instead of claiming that compensation succeeded.

## Evidence

[Cluster failure tests](../tests/test_cluster.py), [shared key rotation](../tests/test_shared_keys.py),
[durable reservations](../tests/test_reservations.py), [TLS checker](../scripts/check_tls.py),
[live callback checker](../scripts/check_webhook_lab.py), and [TCK report](../docs/TCK_REPORT.md).
