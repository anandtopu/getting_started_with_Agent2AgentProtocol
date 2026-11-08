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
