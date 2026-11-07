# Native Java venue agent

Requires Java 17+ and Maven. The official SDK is pinned to 1.5.0.Final and
Quarkus to 3.40.1.1, matching that SDK's published parent build.

From the repository root, run:

~~~console
uv run python scripts/check_java_interop.py
~~~

This compiles and starts the native server on 127.0.0.1:8401 with a randomly
generated bearer token, uses Python protobuf requests to discover and call it,
checks valid quotes and unavailable/invalid guest counts, then stops it.
The first build downloads Maven dependencies; subsequent execution needs no model.

Predict first: does a 150-person request on 2027-06-01 complete? Inspect the
availability calendar, not just room capacities. The reference returns rejected.

The [captured requests and responses](../wire/java.jsonl) are real JSON-RPC traffic.
The SDK owns task IDs, state events and serialization. The executor reads the same
committed venue inventory as Python. Authentication runs on Vert.x, the actual
router used by the SDK. A Jakarta REST filter alone does not protect these routes.
The SDK's default task authorization is fail-closed; Ownership records an
authenticated subject when creating a task and rejects unknown ownership.

For this local lab there is one partner identity and in-memory task/ownership
storage. Production deployments need separate identities, durable ownership and
TLS. No purchase or booking occurs.

Sources: [released SDK server example](https://github.com/a2aproject/a2a-java/tree/v1.5.0.Final/examples/helloworld/server),
[task authorization](https://github.com/a2aproject/a2a-java/blob/v1.5.0.Final/docs/content/dev/authorization.md),
[Quarkus route filters](https://quarkus.io/guides/reactive-routes/).
