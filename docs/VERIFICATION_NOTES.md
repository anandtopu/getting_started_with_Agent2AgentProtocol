# Verification notes

Checked **2026-11-07**. This document is the release's evidence and limitation
record. The expanded course closes the previously listed implementation gaps; external
release status and official TCK exceptions remain explicit below.

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
v1.0.0-preview4 as a prerelease. Its native venue lab now compiles on .NET 10 and
passes actual Python-to-.NET quote, authentication and invalid-input checks.
No stable .NET SDK release is claimed.

## Model configuration

Configured examples are documented as available, not live-tested account access:

- [Ollama qwen3:4b](https://ollama.com/library/qwen3:4b), local and tool-capable.
- [OpenAI gpt-5.6-luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).
- [Anthropic Haiku 4.5](https://docs.anthropic.com/en/docs/about-claude/model-deprecations).
- [Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite).

common/llm.py retains the introductory JSON decision method and adds provider-native
streamed tool calls through common/model_streams.py. All four provider framings are
validated with fragmented offline HTTP streams; the free Ollama model is also run
in CI. Hosted account access is optional and is not claimed as live-tested.
See [the live guide](LIVE_MODELS.md) for commands, framing and bounds.

## Advanced implementation evidence

- The official SDK's VersionedTaskStore and TaskEventStream interfaces back a shared
  SQL snapshot, revision, event journal and callback outbox. Tests inject a transaction
  failure, stale writer, publisher crash, lost connection and expired dispatcher lease.
- SQLite and PostgreSQL run the same cluster suite. Replica ownership, distributed
  request budgets, cancellation and snapshot/subscription races are covered.
- The vendor kit runs durable callback recovery independently of fresh traffic. The
  live Control Room lab verifies signatures and preserves its inbox across restart.
- Hardened Compose uses bearer, API key, OAuth client credentials, OIDC and mTLS.
  Keycloak validates audience isolation; HTTPS clients validate the issuing CA and
  hostname. No TLS verification bypass is used.
- Rotating card keys share an encrypted SQL ring. Restart/replica tests cover overlap,
  expiry and revocation. Wrapping keys remain operator-provided secrets.
- Real PDF and SVG Parts, native model progress, exact twenty-scenario golden checks,
  durable no-charge hold compensation and six-attack security regressions are runnable.
- Six isolated framework workers plus LangGraph use confirmed native execution APIs;
  one official-v1 lifecycle adapter retains identical business semantics.
- The practice bank has 265 tasks across eight types and twenty-five modules. It
  combines small introductory contracts with 115 protocol/workflow/adversarial tasks.
  Every starter fails and every reference solution passes offline. Human design
  rubrics remain deliberately outside automated correctness claims.

## Official conformance evidence

The [official TCK report](TCK_REPORT.md) records the pinned unmodified upstream suite,
all three bindings, its raw score, skips, four reviewed contradictions and nine manual
requirements. The CI gate checks names and diagnostic messages; it does not rewrite
the official result or claim certification. Vendor business behavior is tested by
the course contracts and golden evaluations rather than the TCK fixture executor.

## External limitations and operational scope

The official .NET SDK remains preview4. The implemented native lab is verified;
a stable upstream release cannot be supplied by this repository. Hosted LLM calls
need an account; only the free local provider is live-tested. The TCK has four
upstream contradictions described in its report. None is hidden by a claimed 100%
compatibility score.

The authoring machine has no running Docker engine; GitHub's Linux runners execute
PostgreSQL, Keycloak, Jaeger and both Compose profiles. Network, native-language,
TLS and callback checks run on Linux, Windows and macOS. The hardened profile is a
learning deployment with generated local certificates, not a managed public service.
Its [runbook](../deploy/HARDENED_NETWORK.md) explains certificate renewal, schema
rollout, backups, restore validation and retention. See [validation](VALIDATION_REPORT.md)
for the final revision's counts and CI evidence.
