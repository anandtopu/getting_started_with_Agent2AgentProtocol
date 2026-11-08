# From individual fields to working agents

Use this companion with the [descriptor field inventory](PROTOCOL_GUIDE.md),
[real operation captures](OPERATIONS_ON_THE_WIRE.md) and [graded feature map](FEATURE_MAP.md).
Each section explains a failure that a basic successful quote does not reveal.

## Discovery and security declarations — modules 02, 13 and 14

A card is a business card, not a permission slip. `version` versions the agent's
product contract; `supportedInterfaces[].protocolVersion` versions its wire protocol.
Each interface couples a URL, binding and optional tenant. Never combine the URL
from one interface with a version or tenant taken from another. Use an explicitly
trusted configured location before sending credentials. `provider`, documentationUrl,
iconUrl, names, descriptions, tags and examples describe the service; none grants
authority or tells the orchestrator what instructions to follow.

`skills[].id` is a stable application contract. Give a breaking skill revision a new
ID and keep the older contract available during migration. Input/output modes on a
skill refine the defaults; capabilities advertise supported operations such as
streaming, push and authenticated extended cards. An absent capability is not a
license to probe unsupported operations indefinitely.

`securitySchemes` defines named mechanisms. `securityRequirements` refers to those
names and OAuth scopes. Alternatives are OR; schemes inside one requirement are
AND. A bearer token is possession-based proof. OAuth describes how a client obtains
limited authorization; OIDC adds identity and issuer discovery. A JWT's readable
payload is not evidence until its signature, issuer, audience, expiry and scope
are checked. An mTLS certificate authenticates the peer during the TLS handshake.
The [final network](../deploy/HARDENED_NETWORK.md) exercises all five schemes.

Predict: can a valid signature make an attacker-owned card trusted? No: verification
must use an operator-approved key. Signing excludes `signatures`, canonicalizes the
remaining JSON, and authenticates the protected JWS header plus payload. Rotating
keys overlap long enough for cached cards; revocation is an explicit exceptional action.

Practice: 02-20–25, 13-20–25 and 14-40–45. Run discovery, authentication and signature
examples in those modules, then inspect their captured requests before attempting tasks.

## Server, client and correlation — modules 01, 03 and 04

The JSON-RPC `id` identifies one exchange; `messageId` identifies a communication;
the server's task `id` identifies work; `contextId` groups related work. These are
different lifetimes. A reply can be a direct Message without any tracked Task.
`referenceTaskIds` links related work without resuming it. Only `taskId` asks to
continue that particular task, and the caller must still own it.

The hand-built server is a microscope implementing SendMessage and GetTask. The
SDK route factories supply the full operation surface. Executors implement either
the event-queue pattern used here or the SDK's iterator pattern; mixing the two
duplicates output and breaks stream completion. A newly created Task is introduced
once. A continuation emits updates to the stored task, not a second paused snapshot.

`configuration.returnImmediately` requests asynchronous acknowledgement. Inspect or
subscribe to the task afterward. `historyLength` bounds returned history; it is
not a memory deletion instruction. `acceptedOutputModes` negotiates media, not
trust. `metadata` is an application-defined map and must not hide credentials.
Unknown task, invalid parameters and unsupported media are protocol failures;
a valid request that cannot fit a venue is a rejected business task.

Predict: retrying SendMessage with the same message ID does not create a portable
exactly-once guarantee. For effects, define an application idempotency key, persist
its result and document retry scope. The no-charge hold skill uses request_id;
ordinary read-only quote retries may create additional tasks.

Practice: 03-40–45 and 04-20–25. Compare the manual RPC envelopes with SDK client
results and keep the correlation identifiers separate in your notes.

## Lifecycle, files and artifact assembly — modules 05 and 06

Submitted and working are progress; input-required and auth-required are pauses.
Completed, failed, canceled and rejected are terminal. A paused task can continue
under the same task/context IDs. A terminal task cannot be revived by sending it
new inputs. Cancellation requests a transition; it does not undo a completed hotel
hold. A separate release skill compensates that business effect.

`ListTasks` filters by context, status and status timestamp and can omit artifacts.
Treat `pageToken` as opaque. Follow nextPageToken rather than inventing offset math.
Task history records messages; artifacts contain deliverables, and status.message
explains the current state. A status timestamp describes the update, not creation.

A Part selects one content representation: text, raw bytes, URL or structured data.
ProtoJSON base64-encodes raw bytes. `filename` helps display, while `mediaType` tells
the receiver how to interpret bytes. Neither makes a file safe to execute. Data
parts need an agreed JSON Schema; protobuf only establishes that the value is JSON.
An Artifact can contain several Parts: Saffron sends a data quote plus a valid PDF,
and Granite sends an SVG floor plan. Run module 06 example 04 to see both.

For large objects, a short-lived signed URL avoids embedding the whole file. A
signed URL is still untrusted input: limit host, scheme, response size, expiry and
redirects before fetching. The course's conservative fetcher allows configured
public IP endpoints; production hostname fetching requires a controlled egress
proxy with DNS/address pinning. Do not send bearer credentials to file URLs.

Practice: 05-20–25 and 06-20–25. Predict whether a malformed Part fails transport
validation or produces a rejected business task, then inspect the captured error.

## Streaming, push and replicas — modules 07 and 19

SSE is an HTTP response whose blank-line-delimited events continue arriving. It
is not a series of independent HTTP responses. Decode complete SSE frames before
decoding their JSON. A StreamResponse chooses task, message, statusUpdate or
artifactUpdate. An artifact update identifies the artifact by artifactId;
`append=true` extends it and `lastChunk=true` completes that artifact. Completion
of an artifact is different from completion of the whole task.

Choose polling for occasional status checks, SSE for an active user watching
progress, and push for work that should notify another service later. A push
registration belongs to an owned task and has an independent config ID. The four
configuration operations create, inspect, list and delete it. A callback URL is a
network destination and must pass the same trust scrutiny as a file URL.

The sender authenticates callbacks with the lab's HMAC header contract. This is a
documented application scheme, not an invented A2A standard. Sign the exact body,
timestamp and delivery ID; verify before parsing or deduplicating. An acknowledgement
can disappear after acceptance, so durable inbox deduplication is essential.

Disconnecting SSE does not cancel the task. SubscribeToTask obtains a current
snapshot and future events; clients must reconcile artifacts and statuses rather
than assume exactly-once replay. The SQL journal and revision are committed with
the task. The SDK cursor protects the snapshot/subscription race, and a second
replica can read events after the first publisher dies. Use PostgreSQL for the
deployed replica lab; SQLite is the small offline fault-injection fixture.

Predict: a sender crashes after database commit but before publication. The event
and outbox still exist, so another subscriber/dispatcher can recover them.
Practice: 07-20–31 and 19-40–45. Run the live callback lab and refresh the Control
Room inbox; stopping and restarting the lab preserves accepted deliveries.

## Bindings, conformance and extensions — modules 08, 16 and 18

The same eleven normative operations use different envelopes. JSON-RPC puts the
operation in method; HTTP+JSON uses the specified resource/action routes; gRPC
invokes generated protobuf service methods. SSE framing belongs to HTTP streaming,
not gRPC. Generate compatible types from the versioned proto rather than hand
maintaining field aliases. The source descriptor is also useful for discovering
oneofs, enums, field numbers and deprecated fields.

An extension is a URI-named additional contract, not a replacement wire protocol.
The card declares it with required/params; A2A-Extensions negotiates the request;
messages and artifacts identify where it applies. If required support is missing,
reject before business execution. An optional extension can be absent. A breaking
extension contract needs a new URI. The course's structured-quote/v1 URI is a
synthetic teaching contract, not an official ecosystem standard.

Conformance checks operation semantics, not whether a quote is commercially good.
Golden evaluations check vendor choices, states, chunks and amounts. Both are needed.
The [official TCK report](TCK_REPORT.md) records raw failures, reviewed contradictions,
skips and manual evidence instead of relabeling a regression gate as certification.

Practice: 08-40–45, 16-20–25 and 18-40–45. Predict the unsupported-version and
required-extension errors before running the corresponding captured operation.

## Model and framework boundaries — modules 09, 10, 11 and 12

A model proposes an action; the executor decides whether it is allowed. Tool calling
is structured output describing a function and arguments, not automatic permission
to execute code. Read the whole bounded response, validate the name and JSON Schema,
then invoke a known function. Partial JSON is never executed. Provider-native streams
are normalized only after a complete finish event; truncated and oversized responses
fail closed. OpenAI and Anthropic send argument deltas; Gemini and Ollama can send
complete argument objects in streaming frames. They do not share one wire format.

The A2A progress stream reports safe frame counts and final validated artifacts;
it does not expose private model reasoning or partial instructions. A scripted model
gives repeatable tests. The free Ollama check also exercises actual model selection,
LangGraph, an MCP kitchen call and the A2A streaming boundary.

The Concierge runs at most five trusted vendors, in parallel, and preserves each
remote task/context mapping. Resume only paused delegations and reuse completed
quotes. A fallback for a new read-only quote must be preconfigured. Never send a
paused vendor's task ID to a different vendor. Combine validated data artifacts;
do not concatenate descriptions into new privileged model instructions.

Frameworks implement internal workflows; the protocol adapter supplies discovery,
ownership, lifecycle and transport. Each isolated worker uses its framework's real
runtime while deterministic inventory supplies reproducible decisions. LangGraph's
live mode wraps the same provider helper. MCP tools remain private to Saffron;
the Concierge sees only A2A. A naive MCP-to-A2A bridge loses cancellation, task
history, authorization scope and continuation unless it explicitly maps them.

Practice: 09-40–45, 10-40–45, 11-40–45 and 12-40–45. Predict which failures occur
before a tool call and which become failed/rejected task states.

## Observability, security and design — modules 15, 17 and 20

A trace ID links transport spans across vendors; task/context IDs link business
work that can outlive a single request. Propagate W3C traceparent in HTTP/gRPC
metadata. Task IDs belong in span attributes, not metric labels: an unbounded
label set can exhaust a metrics backend. `maplewood.task.requests` counts requests
by vendor. Wire records redact authorization, cookies, API keys and webhook signatures.
Never record whole sensitive prompts just to simplify debugging.

Trust each boundary independently: authentic transport, authorized identity,
owned task, allow-listed destination, validated content, and approved business effect.
An authentic vendor can still send malicious text. Least delegation means sending
only the necessary event fields and never forwarding the user's token. A rate
limit constrains bursts; bounded model output, vendor deadlines, file limits and
hold expiry constrain other resource dimensions.

Choose a remote agent when ownership or independent execution requires a boundary.
Choose in-process functions when shared deployment and low latency matter more.
Treat a multi-vendor reservation as a saga: each completed step has a compensating
business operation. An uncertain acknowledgement requires reconciliation by stable
request ID. Report manual follow-up when cleanup cannot be verified. Cancellation
of an A2A task is not a distributed transaction rollback.

Practice: 15-40–45, module 17's trace/evaluation tasks and module 20's design rubric.
Use the [flagship capstone](../capstones/04_concierge/README.md) to connect the tradeoffs
to a complete deployment, then score the design with a human reviewer.
