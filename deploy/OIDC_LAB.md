# Obtain credentials outside A2A

OAuth 2.0 is the process used to obtain an access token. OpenID Connect adds
identity metadata, including the issuer's signing keys. A2A uses the resulting
token in an Authorization header; it does not define a login operation.

~~~mermaid
sequenceDiagram
    participant C as Concierge client
    participant K as Local Keycloak
    participant V as OIDC venue
    C->>K: Client credentials (outside A2A)
    K-->>C: Short-lived signed access token
    C->>V: SendMessage + Authorization header
    V->>V: Verify issuer, audience, signature, expiry, tenant, quote scope
    V-->>C: Completed quote task
~~~

Run the usual deployment setup from the repository root:

~~~console
uv run python deploy/prepare.py
docker compose --env-file deploy/secrets/network.env -f deploy/docker-compose.yml up --build -d
uv run python scripts/check_keycloak.py
~~~

The generated, ignored realm file creates a service-account client with a random
secret, a two-minute access token, granite audience, quote scope and maplewood
tenant claim. Password grants and interactive login are disabled for this client.
The checker verifies that wrong client secrets and forged/missing tokens fail,
then sends a real A2A request with the obtained access token.

The extra venue listens on 127.0.0.1:8106; the original six-agent demo keeps its
separate per-vendor credentials. Its Agent Card advertises OpenID Connect.
Public discovery does not grant access. The verifier pins the issuer and JWKS
source through operator configuration and ignores token-controlled key URLs.
Keys are loaded at startup; restart the lab server after a key rotation.

This is a local identity-provider lab. HTTP and Keycloak start-dev are confined
to local development; a public deployment requires HTTPS, production Keycloak
configuration, durable realm storage and a bounded JWKS refresh policy.

Predict first: can the client's own token change its tenant or audience? Editing
either claim invalidates the signature. Even a correctly signed token for another
audience or tenant fails the offline verifier tests.

Sources: [realm import](https://www.keycloak.org/server/importExport),
[service accounts](https://www.keycloak.org/docs/latest/server_admin/index.html#_service_accounts).
