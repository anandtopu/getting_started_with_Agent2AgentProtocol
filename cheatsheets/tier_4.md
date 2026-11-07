# Tier 4: desk reference

**Testing, conformance and debugging** — An offline contract test should observe actual routing and serialized responses. Conformance checks protocol behavior; evaluation checks business outcomes. The official TCK expects a reachable server and is a separate integration job. Course tests do not certify official compliance. Record and redact traffic, inject failures and assert the sequence that a client can observe.

**Observability and evaluation** — A trace groups spans for one distributed request; a span records one operation. Propagate W3C trace context through transports and correlate task IDs without making them authorization credentials. Course attribute names are explicitly application conventions. Golden scenarios check delegations, states and artifacts, not whether prose sounds convincing. Never log tokens or entire sensitive briefs.

**Extensions and versioning** — An extension has a URI, a declaration in capabilities and request-time activation through A2A-Extensions. A required extension is a compatibility obligation. Version selection belongs to the advertised interface. The structured quote extension adds a schema for the deliverable; it must not redefine core task states. Preserve skill contracts or version them when behavior changes.

**Deployment and scale** — A persistent task store survives process loss; an in-memory event queue does not coordinate multiple replicas. The current SDK offers a database event stream and versioned database store, which must be paired correctly. Proxies need streaming timeouts and buffering disabled. Webhook retry requires a durable outbox for crash recovery. Docker packages the process; it does not automatically provide trust or persistence.

**Designing agent networks** — Choose agent boundaries around ownership, independent deployment and durable responsibilities. An in-process function call is often simpler for tightly coupled work. Distributed requests can partially succeed. Compensating actions are new business operations, such as releasing a hold; they are not database rollback across organizations. Write an architecture decision record that states alternatives, failure handling and measurable tradeoffs.

Practice: uv run gym list --module NN; uv run gym next; uv run gym drill.
