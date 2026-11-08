# Release review — cross-file pass

The later [final brief review](FINAL_BRIEF_REVIEW.md) independently revisits this
baseline and records ten additional fixes. The earlier disposition below is kept
as review history, not substituted for the new release gate.

## Scope

Trace requests from Control Room/Concierge through auth, SDK adapters, workflows,
SQL task/event/outbox storage, callback receivers and deployment. Verify configuration
names, ports, certificate identities, database ownership and docs-to-command links.

## Integration findings

| Flow | Evidence | Outcome |
|---|---|---|
| Discovery to authentication | catalog/auth_profiles/card_trust, Keycloak realm and hardened overlay | Five schemes agree with enforcement; audience mismatch rejected |
| HTTP/gRPC to task ownership | BearerGate, AuthenticatedContext, ClusterStore | Tenant plus subject scopes access; IDs alone do not authorize |
| Framework to protocol | FrameworkVendor inherits lifecycle adapter; worker runs isolated native SDK | Identical states/chunks/quote schema; twenty hardened golden plans checked |
| Snapshot to stream recovery | SQL revision/journal with SDK TaskEventStream | Commit-before-publication and second-handler reconnect tests pass |
| Task to callback to acknowledgement | Atomic outbox, fenced lease, independent worker, durable inbox | Lost replies and restart do not duplicate accepted effects |
| Card signing to another replica | SharedCardKeys wrapping secret outside SQL | Common keys survive rotation/restart; revoked keys disappear |
| Model to tool to artifact | Four native parsers, LangGraph, MCP, schema checks | Partial/unsafe calls rejected; progress omits private reasoning |
| Concierge to reservations | Stable request IDs, no-charge holds and tombstones | Uncertain outcome reconciled; failed cleanup needs manual follow-up |
| Observability across transports | Trace middleware/interceptor, call context and task attributes | Shared trace parentage and business identifiers; metrics use bounded labels |
| CI to operating environments | Python 3.11–3.13, six framework workers, three OS native matrix | 26 independent jobs; Docker runs on Linux |
| Lesson to implementation | 25 README/quiz updates, regenerated captures, deep feature guide, capstones | Obsolete incomplete-feature statements replaced with current evidence |

## Validation and residual scope

No unresolved release-blocking integration finding. See [per-file findings](PER_FILE_REVIEW.md)
and [validation evidence](../VALIDATION_REPORT.md). The generated local CA, backups,
retention and future schema migrations require an operator; their procedures are in
[the deployment runbook](../../deploy/HARDENED_NETWORK.md). No cloud service is published
and no real financial or hiring effect is enabled by this learning repository.

## Final cross-file pass

| Boundary traced | Result after correction | Evidence |
|---|---|---|
| Launcher to vendor process to status command | Own inbound token only; peer-token map only in Concierge; status contains names | Launcher isolation regression and every-module live network checks |
| Requested needs to model routing to outbound brief | Model cannot expand scope; vendors and models receive only permitted fields | Scope and data-minimization adversarial tests |
| Remote HTTP stream to task parser to aggregate plan | Time/size bounds, typed task validation, quote contract and per-vendor failure isolation | Slow/oversized/malformed response tests plus golden scenarios |
| Hold commit to malformed acknowledgement to reconciliation | Idempotency-key cleanup releases uncertain hotel/venue holds | Two real durable-ledger tests |
| Signed callback to parser to inbox | Bounded body and schema validation precede accepted effects | Invalid signed event, size-limit, retry and durable inbox tests |
| HTTP/SSE/query data to captured wire files | Credential values redacted before persistence | Multiline stream and signed-query regression |
| Module explanations to exercises to output excerpts | 25 distinct flows and quizzes; refreshed real delegation captures; examples retain standalone execution | Lesson consistency test, gym, examples, notebooks and link checker |

No additional blocking finding remains in these reviewed boundaries after the fixes.
The current pushed revision must still pass the complete 26-job CI matrix. External
limitations and operator responsibilities remain listed in the validation report.

## TCK exception cross-file pass

| Boundary traced | Result | Evidence |
|---|---|---|
| Requirement sample to SDK input validation to binding error | Unsupported media rejects consistently: HTTP 400, JSON-RPC -32005, gRPC INVALID_ARGUMENT; rich identity is preserved | Ordinary-vendor HTTP/servicer tests and four independent loopback wire controls |
| Recommended HTTP content type to official error assertion | Correct recommended type triggers the known assertion before its body check | Pinned source lines and independent 404/400 body validation in the TCK report |
| CORE-SEND-003 definition to generic TCK validator | Missing expected_error selects a success-only check across all three transports | Pinned requirement line 99 and validator line 100; no upstream patch applied |
| Frozen setup to generated fixture to official report | Committed dependencies, clean tracked tree, bounded readiness, fresh JUnit, complete case accounting | Repeated local official runs and the TCK CI job |
| Raw official results to regression gate to published artifact | Four failures remain failures; exact exceptions require independent valid wire responses; incomplete/error/extra-skip runs fail | Gate mutation tests, raw JUnit, summary and tck-wire-evidence.json |

R22–R25 are closed in repository code and documentation. Two upstream defects
still produce four official failures; these are external, explicitly retained
outcomes, not waived protocol obligations or a conformance certification.

## OpenAI request-to-delegation pass

The actual account exposed gpt-4o-mini. Native tool selection and the catering
A2A/LangGraph/MCP path passed, while Concierge initially received HTTP 400 for
the unsupported uniqueItems schema keyword. R26 separates the provider's accepted
schema subset from the application's full schema. The parser still validates the
complete arguments against the original constraints before Concierge can delegate.
Duplicate, empty and unknown vendor selections produce no vendor requests in the
new boundary tests. Property names and literal data are preserved by the schema
projection. All three live acceptance paths subsequently passed; see the
[retained OpenAI evidence](../evidence/openai-live-2026-11-08.json).

## Final brief boundary recheck

| Boundary traced | Correction and acceptance |
|---|---|
| Raw HTTP credential bytes to authentication and routing | Malformed or duplicate bearer/API-key credentials return 401; no verifier or application call is made for invalid credential encoding/ambiguity. A stalled authenticated upload returns 408 after the total body budget. |
| Configured peer to discovery/keys/OAuth/model parser | Shared response collection enforces decoded size before extending the buffer, stops reading on overflow and closes the stream on timeout. The total deadline includes response headers; redirects remain disabled even on a redirect-enabled client. |
| Signed discovery to Concierge task persistence | Signature, transport, typed-card and credential setup failures produce a FAILED event after WORKING instead of escaping the executor. Safe diagnostics identify environment/network/trust configuration without exposing peer text. |
| Live check attempt to published evidence | Each attempt removes the latest success file before configuration or API calls. Expected failures exit nonzero with a recovery hint; successful evidence is written only after native tool selection, A2A/LangGraph/MCP completion and Concierge routing pass. |

R27–R30 close repository-side gaps in the original brief. JSON peer responses are
limited to 1,000,000 decoded bytes and five seconds total by default; JWKS calls
use three seconds. Introductory model JSON uses 512,000 bytes and 45 seconds.
Remote files use 1,000,000 bytes/five seconds and authenticated incoming bodies
1,000,000 bytes/ten seconds. Provider-native streaming retains its separate
existing wire/frame/argument limits and shared 90-second budget. These are course
request budgets, not a claim of operating-system isolation or production capacity.
