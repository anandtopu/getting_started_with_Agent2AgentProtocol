# Release action plan

## Release gate

All findings R1–R21 are implemented. Require Ruff, default no-network tests, all gym
starter/solution checks, all examples/notebooks, links, native interoperability,
PostgreSQL recovery, both Compose profiles, live Ollama and the documented TCK
regression baseline before declaring the pushed main revision validated.

The final review additionally requires `check_network.py --all` on every native
interoperability operating system. See [the fresh brief review](FINAL_BRIEF_REVIEW.md).

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

## Final review closure

R12–R21 closure: credential isolation, requested scope and field minimization,
bounded/validated remote responses, uncertain-hold cleanup, webhook hardening,
wire redaction, Control Room input handling, environment diagnostics, all-module
teaching and complete launcher coverage. Acceptance tests live in
`tests/test_review_boundaries.py`, `tests/test_reservations.py`, `tests/test_course.py`
and the network CI matrix.

## Follow-up backlog

External follow-ups: reassess .NET when a stable SDK is released; remove TCK
exceptions after upstream contradictions are resolved; optionally run hosted-model
checks with an account owner's credentials. These do not change the verified offline
course or replace the operating responsibilities documented in the runbook.

### Follow-up check: 2026-11-08 (America/Chicago)

| Item | Verified status | Next completion condition |
|---|---|---|
| TCK exceptions | Upstream main remains at 104a7b4; only Python/dependency metadata changed after the course pin. Issue [202](https://github.com/a2aproject/a2a-tck/issues/202) and open proposals [203](https://github.com/a2aproject/a2a-tck/pull/203) and [238](https://github.com/a2aproject/a2a-tck/pull/238) cover the defects. Neither proposal is merged. | Review an integrated upstream revision retaining the 1.0.1 error mappings and strict validators, run the entire suite and independent wire controls, then remove only exceptions that genuinely pass. |
| Stable .NET SDK | Official GitHub releases and the NuGet A2A.AspNetCore version index still provide 1.0.0-preview4; no stable package was found. | A stable compatible package is published; update the native lab and pass interoperability on Windows, Linux and macOS. |
| Hosted-model live checks | No OpenAI, Anthropic or Gemini API key was configured in the execution environment, project .env, persistent user environment or repository secrets. No live hosted call was attempted. | Configure the provider keys privately, select accessible models, then run the existing live checker once per provider and retain each provider's evidence. |

The TCK proposals are useful tracking references, not validated replacements for
the pinned suite. PR 203's inspected regression fixture still uses the old HTTP
415 mapping; the released 1.0.1 mapping is 400. PR 238 also changes older media
checks and schema coverage. Adopting either historical branch wholesale could
discard later conformance corrections. Keep the current strict baseline until an
integrated candidate has been reviewed and tested.

The hosted checker already exercises streamed tool selection, A2A/LangGraph/MCP
completion and Concierge routing. Its command and credential setup are in
[the live-model guide](../LIVE_MODELS.md). Missing credentials and unpublished
upstream fixes remain explicit blockers, not passing results.

## TCK investigation closure

| ID | Priority | Owner | Completed action | Acceptance evidence |
|---|---|---|---|---|
| R22 | P2 | Course validation | Exact exception identity/diagnostic and complete report validation | Changed messages, class, extra failures, partial runs, duplicate cases, counters, skips and exit-status mutations fail |
| R23 | P2 | Course validation | Verify every obscured obligation independently | HTTP 404/400 body and content type, JSON-RPC error identity, gRPC binary status and ErrorInfo checked on the same running fixture; ordinary vendor checks also pass |
| R24 | P2 | Course tooling | Preserve upstream lock/source and reject stale evidence or readiness exhaustion | Frozen install leaves git diff empty; timeout regression passes; fresh report generated by real suite |
| R25 | P3 | Course documentation | Correct normative level and record exact upstream causes | Linked source and specification evidence, latest-revision comparison, unchanged raw failure count |

Release gate: complete local checks and all 26 jobs on the pushed revision. Do not
remove these exceptions until the upstream assertions are corrected and reviewed;
never accept unsupported media or change the recommended content type to manufacture
a green official report. Independent controls remain mandatory even after an
upstream correction.
