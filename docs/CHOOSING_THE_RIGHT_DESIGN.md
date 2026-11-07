# Choosing the right design

~~~mermaid
flowchart TD
    A["Who owns this work?"] --> B{"Independent organization or deployment?"}
    B -->|Yes| C["Consider A2A"]
    B -->|No| D["Prefer a local function or in-process agent first"]
    C --> E{"Need continuous progress?"}
    E -->|Yes| F["Streaming"]
    E -->|No| G{"Can the client stay available?"}
    G -->|Yes| H["Polling"]
    G -->|No| I["Authenticated push callback"]
~~~

Choose JSON-RPC for a familiar RPC envelope and broad web compatibility.
Choose HTTP+JSON when HTTP routing and tooling fit your infrastructure.
Choose gRPC when generated contracts and HTTP/2 service infrastructure are useful.
Always select an interface actually advertised by the peer.

A skill should describe a stable business capability with measurable inputs,
outputs and failure behavior. Avoid a separate agent for every function. Multiple
services add latency, credentials, deployments and partial failures.

Before splitting a service, record ownership, expected latency, data sensitivity,
continuation needs, spending approval and compensation. A design that needs a
distributed transaction for every tiny step probably has boundaries that are too small.
