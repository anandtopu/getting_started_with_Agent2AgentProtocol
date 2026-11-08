# Release action plan

## Release gate

All findings R1–R11 are implemented. Require Ruff, default no-network tests, all gym
starter/solution checks, all examples/notebooks, links, native interoperability,
PostgreSQL recovery, both Compose profiles, live Ollama and the documented TCK
regression baseline before declaring the pushed main revision validated.

## Completed fix queue

| IDs | Owner | Completed action | Acceptance |
|---|---|---|---|
| R1, R5, R7 | Course runtime | Atomic cancellation, recovery dispatcher, portable namespaces | SQLite/PostgreSQL cluster and live callback checks |
| R2 | Course identity | Shared encrypted rotating key ring | Cross-replica/restart/expiry/revocation test |
| R3 | Framework adapter | One lifecycle implementation | Native framework matrix and twenty hardened golden plans |
| R4 | Observability | Preserve recording span across SDK boundary | Parentage, ID attributes and metric example |
| R6 | Conformance | Match known failure diagnostics | Unmodified TCK and raw report artifact |
| R8, R9 | Business examples | Explicit reconciliation and invalid-input rejection | Reservation and manual-server regressions |
| R10 | Live model integration | Explicit routing tool prompt and consistent bounded timeouts | Model/workflow/golden tests and actual Ollama end-to-end CI |
| R11 | Stream framing | Separate frame/argument and total-wire byte bounds | Repeated-envelope acceptance and total-size rejection tests |

## Follow-up backlog

External follow-ups: reassess .NET when a stable SDK is released; remove TCK
exceptions after upstream contradictions are resolved; optionally run hosted-model
checks with an account owner's credentials. These do not change the verified offline
course or replace the operating responsibilities documented in the runbook.
