# Release review — per-file pass

## Scope

Baseline main 8b2a61d through the expanded course release. Reviewed authored Python
runtime, transport, persistence, identity, model, capture/check scripts, tests and
Docker/CI configuration. Generated gym folders, captured traffic, lockfiles and
upstream research copies are excluded from line-by-line review; graders, validators
and pinned runtime checks validate their contracts. This is a correctness/security
review of the learning deployment, not external production certification.

## File inventory

| File | Entry line | Responsibility | Disposition |
|---|---:|---|---|
| [.github/workflows/ci.yml](../../.github/workflows/ci.yml) | 1 | Deployment, dependency isolation and CI wiring | Reviewed in release scope; findings below closed |
| [agents/app.py](../../agents/app.py) | 23 | Compose confirmed SDK route factories into a regular FastAPI application. | Reviewed in release scope; findings below closed |
| [agents/catalog.py](../../agents/catalog.py) | 39 | Explicit skill contracts, not instructions inferred from untrusted descriptions. | Reviewed in release scope; findings below closed |
| [agents/concierge.py](../../agents/concierge.py) | 26 | A bounded orchestrator. Remote artifacts are data, never executable instructions. | Reviewed in release scope; findings below closed |
| [agents/concierge_executor.py](../../agents/concierge_executor.py) | 23 | Expose the Concierge over A2A using the same task contract as its vendors. | Reviewed in release scope; findings below closed |
| [agents/executor.py](../../agents/executor.py) | 22 | A task-first executor: paused tasks retain their brief in task metadata. | Reviewed in release scope; findings below closed |
| [agents/framework_vendor.py](../../agents/framework_vendor.py) | 8 | One lifecycle adapter; each framework executes its own internal workflow. | Reviewed in release scope; findings below closed |
| [agents/grpc_server.py](../../agents/grpc_server.py) | 28 | Inkwell: a gRPC-only protocol endpoint plus HTTP card discovery and health. | Reviewed in release scope; findings below closed |
| [agents/langgraph_vendor.py](../../agents/langgraph_vendor.py) | 19 | LangGraph runs Saffron's internal workflow; the official SDK owns its A2A boundary. | Reviewed in release scope; findings below closed |
| [agents/reservations.py](../../agents/reservations.py) | 10 | Add durable hold/release skills around any vendor business runtime. | Reviewed in release scope; findings below closed |
| [agents/server.py](../../agents/server.py) | 20 | Run one local vendor: uv run maplewood --vendor venues --demo. | Reviewed in release scope; findings below closed |
| [common/artifact_files.py](../../common/artifact_files.py) | 6 | Small valid synthetic files for the Parts lesson; no external storage required. | Reviewed in release scope; findings below closed |
| [common/auth_profiles.py](../../common/auth_profiles.py) | 12 | Hardened network: API key, OAuth client credentials, OIDC and mutual TLS. | Reviewed in release scope; findings below closed |
| [common/binding_policy.py](../../common/binding_policy.py) | 10 | Transport policies not supplied by the SDK's route factories. | Reviewed in release scope; findings below closed |
| [common/card_trust.py](../../common/card_trust.py) | 14 | Keys come from operator configuration, never a URL nominated by an untrusted card. | Reviewed in release scope; findings below closed |
| [common/cluster.py](../../common/cluster.py) | 62 | SQL-backed SDK cluster interfaces and an atomic, leased notification outbox. | Reviewed in release scope; findings below closed |
| [common/delivery.py](../../common/delivery.py) | 22 | Restart-safe notification outbox and inbox; delivery is at least once. | Reviewed in release scope; findings below closed |
| [common/frameworks.py](../../common/frameworks.py) | 12 | Run a dependency-isolated framework behind the course's official A2A v1 SDK. | Reviewed in release scope; findings below closed |
| [common/identity.py](../../common/identity.py) | 12 | Validate OIDC access tokens against an operator-pinned issuer, audience and JWKS. | Reviewed in release scope; findings below closed |
| [common/key_rotation.py](../../common/key_rotation.py) | 19 | Automated card-key rotation with overlap and an HTTPS-pinned JWKS endpoint. | Reviewed in release scope; findings below closed |
| [common/llm.py](../../common/llm.py) | 11 | Provider-independent, bounded JSON decisions. Only Tier 2 imports this module. | Reviewed in release scope; findings below closed |
| [common/manual_server.py](../../common/manual_server.py) | 15 | A deliberately small JSON-RPC subset, written without importing an A2A SDK. | Reviewed in release scope; findings below closed |
| [common/model_streams.py](../../common/model_streams.py) | 19 | Provider-native tool streams, normalized only after a complete bounded response. | Reviewed in release scope; findings below closed |
| [common/observability.py](../../common/observability.py) | 15 | W3C trace context crosses HTTP calls; prompts and credentials are never attributes. | Reviewed in release scope; findings below closed |
| [common/remote.py](../../common/remote.py) | 15 | Use a trusted configured binding; never send credentials to a card-supplied URL. | Reviewed in release scope; findings below closed |
| [common/reservations.py](../../common/reservations.py) | 11 | Durable, owner-scoped, idempotent tentative holds; no purchase capability. | Reviewed in release scope; findings below closed |
| [common/saga.py](../../common/saga.py) | 11 | Compensation is a business operation, not cancellation of a completed A2A task. | Reviewed in release scope; findings below closed |
| [common/security.py](../../common/security.py) | 24 | Small security boundaries with explicit policy and no implicit remote trust. | Reviewed in release scope; findings below closed |
| [common/tls.py](../../common/tls.py) | 8 | TLS configuration shared by servers and clients. Verification is never disabled. | Reviewed in release scope; findings below closed |
| [common/vendor_kit.py](../../common/vendor_kit.py) | 25 | A configurable vendor bundle: durable tasks, signed card, streaming and verified push. | Reviewed in release scope; findings below closed |
| [control_room/app.py](../../control_room/app.py) | 1 | Maplewood Control Room. Run: uv run streamlit run control_room/app.py. | Reviewed in release scope; findings below closed |
| [deploy/Dockerfile](../../deploy/Dockerfile) | 1 | Deployment, dependency isolation and CI wiring | Reviewed in release scope; findings below closed |
| [deploy/build_profiles.py](../../deploy/build_profiles.py) | 8 | Reproducible Compose overlays for encrypted and mixed-framework networks. | Reviewed in release scope; findings below closed |
| [deploy/certificates.py](../../deploy/certificates.py) | 14 | Generate a private lab CA and short-lived TLS identities; never commit secrets. | Reviewed in release scope; findings below closed |
| [deploy/docker-compose.yml](../../deploy/docker-compose.yml) | 1 | Deployment, dependency isolation and CI wiring | Reviewed in release scope; findings below closed |
| [deploy/frameworks.yml](../../deploy/frameworks.yml) | 1 | Deployment, dependency isolation and CI wiring | Reviewed in release scope; findings below closed |
| [deploy/hardened.yml](../../deploy/hardened.yml) | 1 | Deployment, dependency isolation and CI wiring | Reviewed in release scope; findings below closed |
| [deploy/keycloak.py](../../deploy/keycloak.py) | 4 | Generate a local service-account realm; never commit its generated client secret. | Reviewed in release scope; findings below closed |
| [integrations/worker.py](../../integrations/worker.py) | 21 | Isolated framework runtime. Input and output are JSON; external networking is blocked. | Reviewed in release scope; findings below closed |
| [scripts/build_advanced_tasks.py](../../scripts/build_advanced_tasks.py) | 11 | Author six distinct acceptance exercises for each advanced protocol feature group. | Reviewed in release scope; findings below closed |
| [scripts/build_boundary_tasks.py](../../scripts/build_boundary_tasks.py) | 12 | Author distinct full-boundary exercises, not copies of small dictionary transforms. | Reviewed in release scope; findings below closed |
| [scripts/build_feature_map.py](../../scripts/build_feature_map.py) | 13 | Build a navigable coverage contract from real files and installed protobuf symbols. | Reviewed in release scope; findings below closed |
| [scripts/build_workflow_tasks.py](../../scripts/build_workflow_tasks.py) | 1 | Distinct workflow exercises using real A2A/MCP routes and provider wire frames. | Reviewed in release scope; findings below closed |
| [scripts/check_hardened.py](../../scripts/check_hardened.py) | 18 | Check the hardened Compose overlay with real Keycloak, HTTPS and gRPC mTLS. | Reviewed in release scope; findings below closed |
| [scripts/check_live_model.py](../../scripts/check_live_model.py) | 10 | Opt-in live model check. Defaults to the free Ollama provider configured in .env. | Reviewed in release scope; findings below closed |
| [scripts/check_tck.py](../../scripts/check_tck.py) | 27 | Run a pinned, unmodified official TCK; retain failures and review known contradictions. | Reviewed in release scope; findings below closed |
| [scripts/check_tls.py](../../scripts/check_tls.py) | 20 | Real TLS and mutual-TLS handshakes, including missing and untrusted identities. | Reviewed in release scope; findings below closed |
| [scripts/check_webhook_lab.py](../../scripts/check_webhook_lab.py) | 15 | Start the live callback lab, verify signed delivery, restart, and check durable state. | Reviewed in release scope; findings below closed |
| [scripts/init_database.py](../../scripts/init_database.py) | 17 | Initialize the pinned schema before starting replicas; credentials come from environment. | Reviewed in release scope; findings below closed |
| [scripts/tck_server.py](../../scripts/tck_server.py) | 24 | Official scenario executor through the course's pinned SDK and transport policies. | Reviewed in release scope; findings below closed |
| [scripts/webhook_lab.py](../../scripts/webhook_lab.py) | 20 | Live signed callback lab, including durable outbox recovery after restart. | Reviewed in release scope; findings below closed |
| [tests/test_artifact_files.py](../../tests/test_artifact_files.py) | 11 | File signatures, PDF cross-reference offsets and actual multi-part A2A output. | Reviewed in release scope; findings below closed |
| [tests/test_auth_profiles.py](../../tests/test_auth_profiles.py) | 31 | Authentication mechanisms, automated rotation and fail-closed JWKS refresh. | Reviewed in release scope; findings below closed |
| [tests/test_binding_policy.py](../../tests/test_binding_policy.py) | 11 | Direct checks for the transport requirements with contradictory TCK assertions. | Reviewed in release scope; findings below closed |
| [tests/test_cluster.py](../../tests/test_cluster.py) | 32 | Independent connections exercise real failure boundaries, not mock databases. | Reviewed in release scope; findings below closed |
| [tests/test_manual_server.py](../../tests/test_manual_server.py) | 8 | The no-SDK microscope distinguishes RPC failures from declined business work. | Reviewed in release scope; findings below closed |
| [tests/test_model_progress.py](../../tests/test_model_progress.py) | 15 | A native provider stream reports safe progress over the actual A2A route. | Reviewed in release scope; findings below closed |
| [tests/test_model_streams.py](../../tests/test_model_streams.py) | 20 | Fragment real provider frames and reject incomplete or unsafe tool responses. | Reviewed in release scope; findings below closed |
| [tests/test_observability.py](../../tests/test_observability.py) | 11 | A propagated header, rather than a local nested block, establishes parentage. | Reviewed in release scope; findings below closed |
| [tests/test_reservations.py](../../tests/test_reservations.py) | 18 | Crash-safe business compensation across independently owned A2A agents. | Reviewed in release scope; findings below closed |
| [tests/test_shared_keys.py](../../tests/test_shared_keys.py) | 12 | A different replica and a process restart must verify cards after rotation. | Reviewed in release scope; findings below closed |

## Findings and completed fixes

| ID | Severity | File | Line | Finding / impact | Resolution and acceptance |
|---|---|---|---:|---|---|
| R1 | P1 | [common/cluster.py](../../common/cluster.py) | 132 | Cancellation used the normal writer CAS, contrary to the SDK cancellation contract. | **Closed.** Use one owner/nonterminal SQL update returning its incremented revision; SQLite and PostgreSQL cluster suite. |
| R2 | P1 | [common/key_rotation.py](../../common/key_rotation.py) | 19 | Process-local signing keys could disagree behind a replica load balancer. | **Closed.** Encrypted shared SQL key ring with CAS rotation; replica/restart/expiry/revocation test. |
| R3 | P1 | [agents/framework_vendor.py](../../agents/framework_vendor.py) | 13 | Separate framework lifecycle code omitted reference behaviors such as AV chunks. | **Closed.** Reuse VendorExecutor and override only internal quote production; hardened network checks twenty golden plans. |
| R4 | P2 | [common/observability.py](../../common/observability.py) | 49 | SDK tracing context could expose a non-recording span, losing task correlation. | **Closed.** Preserve incoming request span through call context and gRPC interceptor; parentage and attribute checks. |
| R5 | P1 | [common/vendor_kit.py](../../common/vendor_kit.py) | 52 | New-event wakeups alone could strand committed callbacks after restart. | **Closed.** Independent bounded recovery loop plus leased outbox and durable verified inbox; live restart checker. |
| R6 | P2 | [scripts/check_tck.py](../../scripts/check_tck.py) | 27 | Allow-listing a failed test by name alone could hide a new failure mode. | **Closed.** Match the exact expected diagnostic as well; retain upstream raw failure and score. |
| R7 | P1 | [common/cluster.py](../../common/cluster.py) | 70 | Long fixture namespaces generated PostgreSQL index names exceeding 63 characters. | **Closed.** Bound namespace length and shorten unique test prefix; PostgreSQL CI passes. |
| R8 | P2 | [common/saga.py](../../common/saga.py) | 11 | A lost first hold response or failed cleanup could escape without reconciliation status. | **Closed.** Release by stable request ID and explicitly return manual_followup_required when cleanup cannot be verified. |
| R9 | P2 | [common/manual_server.py](../../common/manual_server.py) | 15 | Malformed business guest count could raise TypeError as an HTTP 500. | **Closed.** Reject the invalid business request and retain RPC response shape; negative manual-server test. |

## Validation

The [validation report](../VALIDATION_REPORT.md) records the final offline and CI
checks. The preceding 55fb956 revision passed all 26 jobs, including PostgreSQL,
TLS/native languages on three operating systems, live Ollama, and hardened frameworks.
The final revision reruns those gates after teaching/capture updates and final fixes.

## Open questions

R10 (P1), found by the final live-model integration: common/model_streams.py had a
60-second HTTP reader inside a 90-second overall budget, and scripts/network.py
gave model-backed vendors the five-second deterministic-demo timeout. The routing
prompt also did not explicitly distinguish action selection from menu generation.
Closed by matching the reader to the overall deadline, retaining bounded output,
using a 120-second live vendor-call budget, and requesting exactly one native tool
call. The 50 affected offline checks pass; the main CI job repeats the actual
Ollama-to-A2A-to-LangGraph/MCP path and model-selected Concierge plan.

R11 (P2): real Ollama token frames repeat model/timestamp metadata, so a 64 KB total
wire cap could reject a legitimate small tool argument. Frames and arguments retain
their 64 KB limits while total wire bytes have a separate 512 KB bound. New tests
accept legitimate small frames above 64 KB total and reject an excessive total.

No unresolved implementation blocker in the reviewed scope. The official .NET SDK
is preview; the official TCK retains four reviewed contradictions. OpenAI was
subsequently live-validated in the hosted-model review below; Anthropic and Gemini
remain deferred. These are disclosed external evidence limits.

The expanded live gate also exposed model suitability: Qwen3 4B could exhaust the
512-token allowance without a complete routing call. The configured default is now
the publisher-listed tool-capable Qwen2.5 3B non-reasoning model. The gate still
requires actual native tools, a completed A2A/LangGraph/MCP workflow and a model-selected
Concierge plan; no incomplete-response assertion was weakened.

The live small-model test additionally produced a valid function name with an
unexpected tool_args object. Arguments remain strictly validated. A structural
schema error permits one correction request inside the original overall deadline;
unknown tools/enum values and repeated structural errors still fail. Regression
tests prove that no extra fields are silently dropped and no unbounded retry occurs.

## Final brief review of fe6800a

This fresh pass found additional issues despite the earlier green matrix. All
findings below have implemented fixes and focused regression evidence; the final
release still requires the full CI gate described in [the brief review](FINAL_BRIEF_REVIEW.md).

| ID | File | Current line | Reviewed correction |
|---|---|---:|---|
| R12 | [scripts/network.py](../../scripts/network.py) | 26 | Peer credentials now reach only Concierge; status omits secret values. |
| R13 | [agents/concierge.py](../../agents/concierge.py) | 54 | Reject model scope expansion; send only per-vendor fields. |
| R13 | [agents/langgraph_vendor.py](../../agents/langgraph_vendor.py) | 27 | Exclude unrelated private fields from the catering model prompt. |
| R14 | [common/remote.py](../../common/remote.py) | 50 | Bound response bytes and total elapsed request time. |
| R14 | [agents/concierge.py](../../agents/concierge.py) | 140 | Validate Task shape, settled state, continuation identity and quote presence. |
| R15 | [common/saga.py](../../common/saga.py) | 11 | Reconcile malformed acknowledgements after a committed hold. |
| R16 | [common/webhooks.py](../../common/webhooks.py) | 19 | Stop reading oversized bodies and reject invalid signed event schemas. |
| R16 | [common/delivery.py](../../common/delivery.py) | 99 | Reject invalid protobuf event data without a server exception. |
| R16 | [common/security.py](../../common/security.py) | 184 | Reject malformed signature lists and protected-header shapes cleanly. |
| R17 | [common/wire.py](../../common/wire.py) | 57 | Redact structured event streams, signed query fields and URL userinfo. |
| R18 | [control_room/app.py](../../control_room/app.py) | 14 | Validate brief objects and keep discovery cards per vendor. |
| R19 | [scripts/check_env.py](../../scripts/check_env.py) | 14 | Probe local model readiness and report hosted-key presence without values. |
| R20 | [modules/13_authentication/README.md](../../modules/13_authentication/README.md) | 28 | Representative of 25 individually authored module flow/quiz/bug/API/use-case replacements. |
| R21 | [scripts/check_network.py](../../scripts/check_network.py) | 18 | Exercise every module including authentication and listener shutdown. |

## Focused TCK exception review of 59f2324

Scope: the four exceptions, official pinned requirement/validator sources, SDK
error mapping, fixture and ordinary vendor adapters, runner and CI evidence.
Generated official scenarios and tests remain unmodified. Source-level diagnosis
and normative references are in [the TCK report](../TCK_REPORT.md).

| ID | Severity | File | Line | Finding and implemented correction |
|---|---|---|---:|---|
| R22 | P2 | [scripts/check_tck.py](../../scripts/check_tck.py) | 56 | Substring matching could hide an additional diagnostic; the gate also accepted partial reports. Require exact class/name/message, distinct case count, consistent counters/exit, bounded skips and execution of affected cases. |
| R23 | P2 | [scripts/tck_evidence.py](../../scripts/tck_evidence.py) | 103 | Exception text alone could not prove correct error identity or validate the body bypassed by the HTTP assertion. Add independent real-wire checks of status, content type, code, message and structured details before any exception is permitted. |
| R24 | P2 | [scripts/check_tck.py](../../scripts/check_tck.py) | 131 | Plain dependency sync rewrote the upstream lock; readiness exhaustion fell through and stale evidence could survive. Install the exact frozen lock, fail readiness explicitly, clear generated evidence before setup, and verify the tracked tree after execution. |
| R25 | P3 | [docs/TCK_REPORT.md](../TCK_REPORT.md) | 1 | The earlier report called the recommended media type required. State SHOULD accurately, identify missing expected_error as the shared cause of three failures, and document why the latest upstream revision does not fix them. |

Additional files individually reviewed: `scripts/tck_server.py` (all three SDK
bindings and media validation enabled); `common/binding_policy.py` (retained
recommended content type); `agents/app.py` (ordinary handlers also validate media);
`tests/test_binding_policy.py` (full ordinary-vendor errors);
`tests/test_tck_gate.py` (negative mutation controls); `.github/workflows/ci.yml`
(raw reports plus independent evidence and server log); validation and review docs.
No production response was changed merely to satisfy an incorrect assertion.

## Hosted-model acceptance review

| ID | Severity | File | Line | Finding and correction |
|---|---|---|---:|---|
| R26 | P2 | [common/model_streams.py](../../common/model_streams.py) | 19 | The real OpenAI Responses endpoint rejected Concierge's uniqueItems keyword. Project only that unsupported keyword out of a copied wire schema; preserve strict mode and validate returned arguments against the complete original schema. |

Reviewed `agents/concierge.py` for validation before side effects, the stream
parser for validation after complete framing, and `tests/test_model_planning.py`
for meaningful rejection tests. Five new cases cover real Concierge schema
construction, duplicate/empty/untrusted selections, original-schema immutability,
property names and literal data. The live OpenAI checker passed with gpt-4o-mini;
the retained evidence contains no credentials. Anthropic/Gemini live checks were
deferred explicitly by the user, and their request paths remain unchanged.

## Final brief recheck of 6ccd1fb

The 2026-11-08 recheck traced the original brief's bounded networking, explicit
terminal task state and friendly learner diagnostics requirements. These additional
findings are fixed; no conformance requirement or exception gate was relaxed.

| ID | Severity | File | Line | Finding and implemented correction |
|---|---|---|---:|---|
| R27 | P2 | [common/security.py](../../common/security.py) | 61 | UTF-8 header decoding and ASCII-only constant-time comparison raised exceptions for malformed credentials; duplicate credentials used the last value. Decode HTTP bytes safely and reject non-ASCII or duplicate credentials with 401 before verification or routing. |
| R28 | P2 | [common/http_limits.py](../../common/http_limits.py) | 18 | Per-read timeouts allowed a peer to keep auxiliary downloads open; several JSON paths buffered unbounded responses. Apply a shared total deadline and decoded-byte limit to discovery, card/OIDC keys, OAuth tokens and introductory model replies; file downloads use the same byte collector and a total deadline. Authenticated request bodies also have a total deadline. |
| R29 | P2 | [agents/concierge_executor.py](../../agents/concierge_executor.py) | 47 | Discovery and client setup happened after WORKING but outside the failure handler. Include them in the terminal-state boundary, parse verified cards into typed SDK messages and emit FAILED with a safe recovery hint. |
| R30 | P2 | [scripts/check_live_model.py](../../scripts/check_live_model.py) | 64 | Expected provider failures printed tracebacks and left earlier success evidence in place. Clear the latest report before starting, preserve nonzero failure exit, print a bounded safe diagnostic and write success only after all acceptance paths pass. |

Individually reviewed changed consumers: `common/auth_profiles.py`,
`common/card_trust.py`, `common/identity.py`, `common/llm.py`,
`common/security.py`, `agents/concierge_executor.py`, the HTTP helper and live checker.
Malformed JWKS shapes now fail closed. Existing streamed-model budgets, pinned
trust, TLS verification, local schema validation and actual transport selection
remain intact. `tests/test_final_boundaries.py` adds 29 adversarial cases; existing
provider mapping, identity rotation, ownership and protocol tests supply positive
compatibility coverage. Documentation was reconciled with these exact limits.
