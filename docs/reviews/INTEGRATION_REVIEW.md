# Release review — cross-file pass

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
