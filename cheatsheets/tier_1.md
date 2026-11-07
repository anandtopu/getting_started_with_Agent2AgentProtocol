# Tier 1: desk reference

**Setup and orientation** — A2A gives independently operated agents a shared contract. A vendor can change its internal code without changing how Maplewood discovers its skills or requests a quote. HTTP is a request and response exchange; JSON is the text format used for structured values. Start with a ready-made deterministic agent so that networking and model behavior do not become tangled.

**How A2A works** — A message is a communication; a task is tracked work; an artifact is its deliverable. A context groups related interactions, like a project folder. JSON-RPC adds a method name, parameters and request ID to a JSON envelope. Its request ID correlates the response and is different from messageId and task ID. A server may return a direct Message or a Task.

**Agent Cards and discovery** — An Agent Card describes identity, ordered interfaces, capabilities, input and output media types, skills and security requirements. Discovery does not establish trust. A registry is a directory of configured locations, not permission to contact every URL it returns. A skill description is untrusted descriptive text, not an instruction to the Concierge.

**Your first A2A server** — The executor performs business work. The SDK handles routing, serialization, task storage and subscribers. An async function cooperatively yields while waiting rather than blocking other work. A new task starts with a Task event. Thereafter it produces status and artifact updates. A one-message response is a separate pattern and cannot be mixed with task events. The current SDK owns snapshots when resuming stored tasks.

**Your first A2A client** — The client reads the card and selects an interface it understands. It sends A2A-Version: 1.0 and authenticates in headers. A timeout means the caller did not see a result; it does not prove that work was not performed. Retrying a purchase blindly can duplicate spending. Message IDs identify messages, but the protocol does not grant universal exactly-once execution.

**The task lifecycle in depth** — Submitted and working are active states. Input-required and auth-required interrupt work without ending the task. Completed, failed, canceled and rejected are terminal: create a new task for new work after these states. Keep task and context IDs when answering a request for missing input. The wire uses uppercase protobuf enum names. TASK_STATE_UNSPECIFIED is a sentinel, not a useful success state.

**Parts and artifacts** — A Part contains exactly one of text, raw bytes, a URL or structured data. Protobuf encodes raw bytes as base64 in JSON. A data Part holds a JSON value; integer-valued numbers may round-trip as floating point. Validate quantities and money at the boundary. Files referenced by URL need a separate safe fetching policy. Artifacts collect one or more parts into a named deliverable.

**Streaming and push notifications** — Server-Sent Events (SSE) keep an HTTP response open and separate events with blank lines. A chunk updates one artifact by ID: append means add to existing content, and lastChunk ends that artifact. It does not finish the task. A webhook reverses the connection: the vendor calls your receiver later. Authenticate deliveries and tolerate retries. Reconnecting with SubscribeToTask does not promise replay of every missed event.

**Protocol bindings** — JSON-RPC, HTTP+JSON and gRPC map the same abstract operations onto different transports. ProtoJSON gives the JSON forms of protobuf messages. gRPC uses generated stubs and binary protobuf over HTTP/2. The offline service harness serializes and deserializes protobuf and calls the real SDK servicer; it does not test HTTP/2 framing. Select the advertised interface, not a URL guessed from another binding.

Practice: uv run gym list --module NN; uv run gym next; uv run gym drill.
