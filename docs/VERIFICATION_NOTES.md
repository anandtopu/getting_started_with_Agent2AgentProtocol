# Verification notes

Checked **2026-11-07**. This document is the release's evidence and limitation
record. It does not claim the complete original production-course brief is finished.

## Specification and dependencies

- Stable specification: [1.0.1](https://github.com/a2aproject/A2A/releases/tag/v1.0.1).
  The advertised interface and request header use **1.0**, not the patch release.
- Normative definition: [versioned a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).
- Read the complete [What's new overview](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/whats-new-v1.md)
  and [changelog](https://github.com/a2aproject/A2A/blob/v1.0.1/CHANGELOG.md).
- Read the [Python migration guide](https://github.com/a2aproject/a2a-python/blob/v1.3.0/docs/migrations/v1_0/README.md).
- Official Python SDK: [1.3.0](https://pypi.org/project/a2a-sdk/1.3.0/).
- Official JavaScript SDK: [1.3.0 registry metadata](https://registry.npmjs.org/@a2a-js/sdk/1.3.0).
- [Package observations](PACKAGE_VERSIONS.md) record all queried package versions.
  uv.lock and package-lock.json record actual dependency resolution.

## Corrections and API choices

The overview contains claims that are not present in the versioned protobuf.
The implementation uses statusUpdate/artifactUpdate wrappers, pageSize/pageToken/
nextPageToken, append/lastChunk and Task.status.timestamp. It does not invent
createdAt, lastModified or artifact index fields. Deprecated OAuth flows remain
in the schema for compatibility; the course does not recommend them.

The card's well-known path and signatures existed before v1. The course therefore
does not describe them as newly introduced by v1.

SDK APIs were inspected in the installed 1.3.0 source, then exercised:
route factories, DefaultRequestHandler, AgentExecutor, RequestContext, EventQueue,
protobuf types, helpers, create_client, ClientConfig, GrpcHandler,
InMemoryTaskStore, DatabaseTaskStore and push configuration/sender interfaces.

SDK 1.3.0 owns the stored task snapshot when resuming interrupted work.
Re-enqueuing the paused Task caused the blocking call to return its old paused
state. The executor introduces a Task for new work and emits updates on continuation.
This adjustment is covered by an in-process continuation test.

The [Inspector](https://github.com/a2aproject/a2a-inspector) is now a standalone
Go binary with embedded UI, not an npm-installed application.
The [official TCK](https://github.com/a2aproject/a2a-tck) expects a reachable server.
Course contract tests are not a substitute for a passing official TCK report.

## Framework compatibility

Registry metadata was checked for Google ADK 2.14.0, LangGraph 1.2.20,
Strands Agents 1.64.0, Pydantic AI 2.66.0, CrewAI 1.15.37,
Microsoft Agent Framework 1.25.0 and BeeAI 0.1.86.

| Framework | Evidence at check time | Course status |
|---|---|---|
| Google ADK | BaseAgent and InMemoryRunner verified | Isolated worker, official v1 boundary, pause/resume tested |
| LangGraph | 1.2.20 StateGraph verified in the installed package | Working official-v1-SDK adapter, MCP tool and pause/resume tests |
| Strands | Agent.invoke_async verified; native A2A extra pins SDK below 0.4 | Isolated worker behind v1 boundary, tested |
| Pydantic AI | slim 2.66.0 Agent and FunctionModel verified | Isolated worker behind v1 boundary, tested |
| CrewAI | Crew.kickoff_async verified; native A2A extra requires SDK 0.3.x | Isolated worker behind v1 boundary, tested |
| Microsoft Agent Framework | core 1.25.0 WorkflowBuilder and executor verified | Isolated worker behind v1 boundary, tested |
| BeeAI | Workflow verified; native A2A extra pins SDK below 0.4 | Isolated worker behind v1 boundary, tested |

Do not install incompatible native adapters into the core environment. The six
isolated workers use each framework's real execution API behind the official v1
SDK boundary. All pass authenticated A2A continuation checks on Windows and Linux.
This is not an exhaustive cross-product of framework-native A2A clients and servers.
See [the integration matrix](../integrations/README.md).

Official Go v2.8.0 and Java v1.5.0.Final releases were observed. The Go venue agent
is compiled and its authenticated quote is checked against the Python inventory.
Java now compiles and passes native authentication, ownership, quote and rejection
checks with SDK 1.5.0.Final and Quarkus 3.40.1.1. A Vert.x route filter is required:
Jakarta REST filters do not protect this SDK's router. The official .NET release list reports
v1.0.0-preview4 as a prerelease; no stable .NET integration is claimed.

## Model configuration

Configured examples are documented as available, not live-tested account access:

- [Ollama qwen3:4b](https://ollama.com/library/qwen3:4b), local and tool-capable.
- [OpenAI gpt-5.6-luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).
- [Anthropic Haiku 4.5](https://docs.anthropic.com/en/docs/about-claude/model-deprecations).
- [Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite).

common/llm.py implements bounded HTTP JSON decision calls for all four providers.
The teaching tool loop validates model decisions before invoking deterministic
functions. This is not a complete provider-native streaming tool-call implementation.

## What the current tests establish

- Actual JSON-RPC and HTTP+JSON requests through the official SDK's ASGI routes.
- Deterministic quote artifacts for five vendors.
- Catering interruption and continuation, stream ordering, chunks and cancellation.
- Protobuf roundtrip calls to the real gRPC servicer without a listening port.
- A deployed gRPC-only Inkwell endpoint with authentication, plus the Concierge's
  HTTP-to-gRPC delegation and signed-card trust checks.
- Real LangGraph and MCP SDK execution inside Saffron's A2A boundary.
- OAuth/OIDC token-verifier negative cases, SQLite restart continuation, HTTP trace
  propagation, bounded fallback, explicit hold compensation and 20 golden scenarios.
- The vendor kit combines signed cards, authentication, durable tasks and verified
  push; the hiring capstone coordinates three A2A agents and pauses for consent.
- Missing-credential rejection, owner isolation, signature tampering rejection,
  unsafe file URL rejection and webhook replay checks.
- Every gym starter fails and every reference solution passes its task checks.
- Module files and cleared notebooks are structurally checked.

The gym currently has 133 core tasks and 24 bonus tasks across eight types.
Build/Fix/Conformance tasks share a small contract within each module; this is
introductory practice, not the requested deep bank of six distinct tasks per feature.
Seven additional tasks use real protocol and adversarial acceptance checks for
continuation, streaming, gRPC, authentication, signing, SSRF and minimal disclosure.
Design checks are structural only; human rubric review is mandatory.

## Remaining gaps against the original brief

- A stable .NET agent; upstream currently provides a preview.
- Complete SDK/feature coverage and distinct Build, Secure and Interop tasks testing
  full agents rather than only small contract transformations.
- Production OAuth/OIDC/mTLS wiring, live Keycloak realm/client configuration,
  rate limiting, durable replay storage and automated key rotation.
- The hold-compensation lab is separate from the live Concierge's quote workflow.
- All-vendor golden state assertions, stream-disconnect/resubscription chaos,
  and durable multi-replica delivery. HTTP and gRPC trace parentage are now tested.
- Complete production capstones, advanced model-native streaming/tool calling,
  and a successful official TCK run.

All eleven operations have actual JSON-RPC, HTTP+JSON and in-process gRPC captures;
the terminal-task SubscribeToTask error is deliberately included.

Docker has no running engine on the authoring machine. GitHub's Linux runner
built and ran the network and verified PostgreSQL restart continuation and Jaeger
trace export through its v3 API.
See [the validation report](VALIDATION_REPORT.md) for the final CI result.
Real model calls and official TCK execution were not verified.
