# Container lab

This lab packages six authenticated agents and starts supporting Postgres,
Keycloak and Jaeger services. The current reference agents use in-memory stores;
supporting services are included for the production exercises and are not claimed
to be integrated automatically.

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

The engine was unavailable during authoring; this configuration needs an actual
Docker run before it can be considered verified. A production deployment also
needs TLS, OAuth/JWT verification, persistent task and event stores, migrations,
backups, reliable callback outboxes, tenant tests and operational runbooks.
