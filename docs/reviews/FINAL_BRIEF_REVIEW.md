# Final review against the original brief

## Scope and method

Reviewed baseline `fe6800a` afresh against the user's original 15-section brief,
rather than accepting the earlier completion report as evidence. This is a new
requirements and adversarial review of the same repository, not third-party
certification. The review covers the learner-facing course, launcher, Control Room,
protocol/security boundaries, model routing, persistence, compensation, deployment
configuration and validation commands.

Pass 1 inspected individual runtime files and all 25 module README/quiz pairs.
Pass 2 traced credentials from launcher to vendor, user scope through model selection
and dispatch, remote replies into aggregate plans, uncertain holds into cleanup,
callback bodies into verification/storage, and wire traffic into published logs.
Generated task folders and native dependency lockfiles were checked through their
graders and runtime matrix rather than claimed as line-by-line manual review.

The release pointers were checked again on 2026-11-08 UTC: specification
[1.0.1](https://github.com/a2aproject/A2A/releases/tag/v1.0.1) and Python SDK
[1.3.0](https://github.com/a2aproject/a2a-python/releases/tag/v1.3.0) remain the
targeted stable releases. No dependency migration was necessary.

## New findings and completed fixes

| ID | Severity | Finding at the reviewed baseline | Fix and acceptance evidence |
|---|---|---|---|
| R12 | P1 | Every local vendor inherited the Concierge's peer-token map; status printed runtime secrets | Only Concierge receives peer credentials; status reports names only. `test_launcher_separates_credentials_and_redacts_status` |
| R13 | P1 | A model could select a trusted but unrequested vendor, and all vendors received dietary/room fields | Enforce requested scope before any call and minimize fields per vendor. `test_model_cannot_delegate_outside_requested_scope`, `test_each_vendor_receives_only_needed_fields` |
| R14 | P1 | Remote response bodies lacked a total byte/deadline bound; malformed task shapes could abort the aggregate; completed tasks without quotes counted as success | Bound HTTP response consumption, parse the real Task type, require final/paused state and quote artifacts, preserve continuation identity and isolate failures. Response-limit, deadline and malformed-reply regressions |
| R15 | P2 | A committed hotel hold with a malformed confirmation bypassed compensation; malformed venue confirmations could be accepted | Treat malformed acknowledgements as uncertain outcomes and reconcile by stable request key. `test_malformed_confirmation_after_commit_is_compensated` exercises both vendors against the durable ledger |
| R16 | P1 | Introductory webhook receiver read an unbounded body before applying its limit; invalid signed protobuf data raised an uncaught error; sender omitted connection-error retry | Bound reads while receiving, reject invalid event data and retry transient transport failures. Size, malformed-event and connection-retry regressions |
| R17 | P1 | Wire redaction covered JSON but not SSE data or signed query credentials | Redact multiline event data, credential query fields and URL userinfo. `test_wire_redacts_multiline_events_and_signed_query_secrets` |
| R18 | P2 | Control Room malformed JSON could crash the push flow; switching vendors could display a stale card | Validate object-shaped briefs consistently and store cards by vendor. Streamlit AppTest checks invalid JSON and non-object input without a crash |
| R19 | P2 | Environment checker omitted actual Ollama/model readiness, hosted-key presence and the gRPC port; launcher errors could produce a traceback | Add bounded local model probing, secret-free key diagnostics, gRPC port checks and friendly argument/process errors. Diagnostic regression and real CLI checks |
| R20 | P2 | Module diagrams, bug tables and quizzes repeated generic scaffolding; use cases lacked specific observed excerpts; eight examples lacked notebook counterparts; some documents contained encoding damage and stale claims | Author 25 distinct flows, explanations, API tables, six-question quizzes, bug tables and use cases. Add all eight notebook counterparts and completeness regression, synchronize quizzes, refresh affected real captures and repair encoding |
| R21 | P2 | CI checked only three module numbers, leaving the module-04 authentication transition and other launcher configurations inferred | `check_network.py --all` now starts, exercises and stops every core module, checks authentication from module 04, and verifies listeners close. Run on all three native-interoperability operating systems |

The exact changed functions and line references are recorded in the
[per-file pass](PER_FILE_REVIEW.md); boundary conclusions are in the
[integration pass](INTEGRATION_REVIEW.md).

## Original brief coverage

| Brief requirement | Reviewed implementation and evidence |
|---|---|
| Public repository, current specification and SDK | Public main branch; pinned lockfiles; verification notes; generated protobuf types; migration-only legacy documentation |
| Deterministic, inexpensive, cross-platform learning | Tier 1 without provider imports; default socket-blocked pytest; scripted gym models; Windows/Linux Python matrix and three-OS native/network matrix |
| Maplewood data and vendor network | Seeded committed inventory, twenty event fixtures, golden scenarios, five vendors and Concierge; seven framework runtimes and native language labs |
| Complete Practice Gym | 265 tasks, eight types, at least four types and three levels per module; trusted graders; failing starters and passing references; progress, hints, reset and drills |
| Every module's template and teaching | 25 modules with at least three examples, captured wire records, specific diagrams and quizzes, practical use cases, bug practice and notebook counterparts |
| Actual protocol behavior | All eleven operations captured across three bindings; manual server/client microscopes; task lifecycle, Parts, files, artifacts, streams, callbacks, extension and version tests |
| Live models and orchestration | Four provider-native parsers; real Ollama tool selection, A2A/LangGraph/MCP completion and Concierge planning; requested-scope enforcement and deterministic arithmetic |
| Authentication, identity and malicious peers | Five auth schemes in hardened deployment; owner/tenant isolation; signed cards and rotation; egress controls; bounded inputs/outputs; redacted logs; explicit approval state |
| Recovery and production teaching | Atomic SQL task/event/outbox persistence, replica reconnect, fenced retries, durable inbox, reservation compensation and operating runbook |
| Control Room and local tooling | Discovery, per-vendor cards, messages, streamed events/artifacts and verified webhook inbox; all-module launcher test; model/key diagnostics |
| Capstones and course-wide references | Five reference capstones, acceptance checks, diagrams, security reviews and rubrics; learning schedules, feature map, protocol guide, glossary, bugs, migration and cheatsheets |
| Final validation and publication | Locked sync, Ruff, offline tests, gym, all examples/notebooks, online links, all-module network checks and 26-job CI gate; push only the reviewed source and documents |

## Acceptance and residual scope

The release gate is the complete local suite plus **all 26 CI jobs on the pushed
revision**, including the real-model workflow and both container deployments.
The [validation report](../VALIDATION_REPORT.md) records counts and the main-branch
workflow provides the final revision's result. A previous green run does not satisfy
this review's gate.

The official TCK still has four specifically documented upstream contradictions;
the raw report is retained and CI rejects any unexpected failure. The .NET SDK is
still a preview, hosted model providers are tested offline unless account credentials
are supplied, and operating a production deployment still requires an operator.
Those qualifications are not relabeled as certification. Local subprocesses run as
the same user: environment minimization reduces accidental credential exposure but
does not claim OS isolation from hostile code with access to the workspace.
