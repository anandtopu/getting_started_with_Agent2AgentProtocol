# Integration labs and what they prove

The short early exercises isolate concepts. These labs connect the components and
assert behavior across an actual protocol boundary. All Python checks below run
without model keys. Only the explicitly labeled network commands bind local ports.

## Three bindings and signed discovery

Start uv run python scripts/network.py up --module 08. Granite, Saffron, Brightline,
Northstar and the Concierge use HTTP. Inkwell exposes only gRPC operations on 8204;
its HTTP listener on 8104 serves the public card and health check.

The launcher creates separate bearer credentials and Ed25519 signing keys for each
agent. The Concierge reads public cards from configured addresses and verifies them
against separately provisioned keys before delegation. It never follows an arbitrary
endpoint or key URL supplied by a card.

Run uv run python scripts/check_network.py --module 08 to start, exercise and stop
the complete network. Run it without another copy of the network already running.
The check asserts that Inkwell rejects an unauthenticated gRPC request and has no
HTTP send-message route.

[Server](../agents/grpc_server.py) · [trust policy](../common/card_trust.py) ·
[all operation captures](OPERATIONS_ON_THE_WIRE.md)

## LangGraph and private MCP tools

~~~mermaid
sequenceDiagram
    participant C as Concierge
    participant A as Saffron A2A boundary
    participant G as LangGraph workflow
    participant K as Internal MCP kitchen
    C->>A: Event brief
    A->>G: Validated brief
    G->>G: Bounded model tool decision
    G->>K: available_menu guest count
    K-->>G: Kitchen inventory
    G-->>A: Structured quote or missing input
    A-->>C: A2A artifact or input-required
~~~

The framework chooses how to perform work; the SDK handles task identity,
serialization and transport. MCP exposes an internal tool, while A2A exposes the
vendor's externally meaningful work. A tool response alone is not an A2A task.

Predict: if the model requests a quote without dietary counts, should the server
produce an estimate? Run:

~~~console
uv run python modules/11_framework_integrations/examples/04_langgraph_vendor.py
uv run python modules/12_a2a_mcp/examples/04_internal_kitchen.py
uv run pytest tests/test_langgraph.py tests/test_mcp.py
~~~

The first command pauses, then completes the same task after a second turn. Required
input and allowed tools are enforced by code even when the scripted model proposes
something else. Replace ScriptedModel with common.llm.create_model() to use the
configured provider; account access and model quality are separate live checks.

MCP 2.3.0 uses Client(server) for its real in-memory connection and MCPServer from
mcp.server. This is not the older nested-session API.

Sources: [MCP v2 guide](https://py.sdk.modelcontextprotocol.io/whats-new/) and
[LangGraph graph API](https://reference.langchain.com/python/langgraph/graph).

## Continuation, fallback and compensation

The Concierge preserves each remote task and context ID. Completed quotes are
reused; paused tasks resume on their original server. A transport failure may use
an operator-configured backup for a new read-only quote. It never transfers an
existing paused task ID to a different server.

Compensation is a separate business operation. The hold lab creates a no-charge
hotel reservation, observes a venue rejection and explicitly releases the hotel
hold. Sending CancelTask to the already completed hold task would not undo the
business action. Releasing the same hold twice is safe.

~~~console
uv run pytest tests/test_recovery.py tests/test_compensation.py
uv run python modules/20_designing_agent_networks/examples/03_compensate.py
~~~

[Recovery](../agents/concierge.py) · [hold executor](../agents/holds.py) ·
[compensation](../common/saga.py)

The hold ledger is in memory and is a teaching example. Durable outboxes,
reservation expiry and recovery after a process crash remain deployment work.

## Identity, tracing and persistence

OIDC tests use locally generated RSA keys and real signed JWTs. Wrong issuer,
audience, scope, tenant, expiry, signature or attacker-nominated key URL is rejected.
The [Keycloak lab](../deploy/OIDC_LAB.md) additionally obtains real service-account
tokens and uses them with a separate OIDC venue. The primary network retains its
per-vendor credentials.

Trace tests inject W3C traceparent into HTTP headers and gRPC metadata and extract
it at each receiver. Parent span IDs are asserted. Database tests close the original
SQLite engine and handler, create new ones, then resume the stored task.

~~~console
uv run pytest tests/test_identity.py tests/test_observability.py tests/test_persistence.py
uv run pytest tests/test_golden.py
~~~

The 20 golden cases assert delegation, exact quote artifacts and state/artifact
sequences for every vendor, including incomplete and conflicting briefs.

## Native language interoperability

TypeScript uses the official SDK 1.3.0; Go uses the official SDK v2.8.0.
Both checks compile or type-check the agent, start it on loopback, send real
authenticated Python requests and terminate the owned process.

~~~console
npm ci
npm run typecheck
uv run python scripts/check_typescript_interop.py
uv run python scripts/check_go_interop.py
uv run python scripts/check_java_interop.py
~~~

Go requires a Go 1.26 toolchain. The initial dependency download needs internet;
the subsequent exchange is local. Java uses official SDK 1.5.0.Final and requires
Java 17+ and Maven. The .NET official
release list currently identifies v1.0.0-preview4 as a prerelease. Its
[native lab](../modules/bonus/B2_other_sdks/dotnet/README.md) is implemented and tested,
but this course does not represent the package as stable.

[Go source](../modules/bonus/B2_other_sdks/go/main.go) ·
[official .NET releases](https://github.com/a2aproject/a2a-dotnet/releases)
