# Container lab

This lab packages six authenticated agents with signed cards. PostgreSQL stores
each vendor's tasks in a separate table, and OpenTelemetry exports HTTP request
traces to Jaeger. Inkwell uses gRPC operations and propagates trace metadata.
Keycloak imports a service-account realm and authorizes an additional OIDC venue;
see [the token acquisition lab](OIDC_LAB.md).

Generate unique local secrets:

~~~console
uv run python deploy/prepare.py
docker compose --env-file deploy/secrets/network.env -f deploy/docker-compose.yml up --build
~~~

Stop with the same Compose command ending in down. Add --volumes only when you
explicitly want to delete the lab's database data.

All published ports bind to 127.0.0.1. Containers listen on their internal
interfaces so the private Compose network can route between them. Do not expose
the development identity server or Jaeger UI publicly.

Run uv run python scripts/check_compose.py after startup to check the aggregate
plan, restart Saffron and resume its PostgreSQL-backed task, and query Jaeger v3
for exported traces. GitHub CI runs this integration on Linux; see the
[validation report](../docs/VALIDATION_REPORT.md).

Continue to [the hardened network](HARDENED_NETWORK.md) for TLS, five different
authentication schemes, real framework workers, shared key rotation, atomic event
and outbox persistence, and the backup/restore and rollout runbook. The base Compose
file is the incremental bearer-token lesson; the overlays are the final deployment.
