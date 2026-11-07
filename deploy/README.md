# Container lab

This lab packages six authenticated agents with signed cards. PostgreSQL stores
each vendor's tasks in a separate table, and OpenTelemetry exports HTTP request
traces to Jaeger. Inkwell uses gRPC operations. Keycloak also starts, but realm,
client and token acquisition are not yet wired into the live network.

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

Production still requires TLS, identity-provider wiring, durable event delivery,
migrations, backups, reliable callback outboxes and operational runbooks.
Task persistence alone does not make in-flight streams survive a replica loss.
