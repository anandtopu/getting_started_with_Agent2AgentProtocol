# Validation report — expanded course release

Repository: [getting_started_with_Agent2AgentProtocol](https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol)

The previously listed implementation gaps are now addressed. The course contains
25 modules, 265 graded tasks, 83 module examples, 25 use cases, 25 notebooks and
five capstones. External SDK/TCK limitations remain explicit below; this report
is evidence of the learning deployment, not an external production certification.

## Executed checks

| Check | Evidence |
|---|---|
| Offline Python | 774 tests; application sockets disabled; A2A deprecations are errors |
| Gym | 265 starters fail and 265 solutions pass; 25 modules, eight types, at least four types and three levels per module |
| Examples and notebooks | 118 standalone commands (83 examples, 25 use cases, 10 capstone starter/reference commands) and all 25 notebooks |
| Style | Ruff lint and formatting; no banned current-track legacy APIs |
| Links | 1,688 local references and 79 external URLs checked after the TCK investigation |
| Protocol | All eleven operations captured for JSON-RPC, HTTP+JSON and protobuf service boundaries; real network gRPC separately checked |
| Golden scenarios | All twenty fixtures check exact vendor states, chunks, artifact IDs and quotes; hardened framework deployment also checks every golden plan |
| Persistence and replicas | SQLite/PostgreSQL CAS, atomic task/event/outbox rollback, publisher crash, second-handler stream reconnect, owner isolation |
| Delivery | Durable signed inbox, lost acknowledgement, expired lease fencing, bounded retries, independent restart recovery and live Control Room lab |
| Identity and TLS | Five vendor auth schemes; real Keycloak audience rejection; HTTPS CA/hostname validation; missing mTLS certificate rejected |
| Signing keys | Encrypted shared SQL ring; rotation overlap, expiry, revocation, replica agreement and restart |
| Models | Four provider-native stream parsers tested offline; real free Ollama qwen2.5:3b tool calls in CI |
| Frameworks | LangGraph plus six isolated real runtimes; twelve Windows/Linux worker jobs and mixed-framework Docker deployment |
| Languages | Native TypeScript, Go, Java and official .NET preview; authenticated Python interoperability on Windows, macOS and Linux |
| Observability | HTTP/gRPC trace propagation, task/context span attributes, bounded vendor metric labels, all six services exported to Jaeger |
| Business recovery | Idempotent no-charge hotel/venue holds, uncertain-response cleanup, compensating release and explicit manual follow-up |
| Review | [Per-file](reviews/PER_FILE_REVIEW.md), [cross-file](reviews/INTEGRATION_REVIEW.md) and [closed action plan](reviews/ACTION_PLAN.md) |
| Final brief review | [Fresh requirements and adversarial review](reviews/FINAL_BRIEF_REVIEW.md); ten additional findings fixed, 25 lesson rewrites, every core module's network lifecycle checked |
| TCK exception investigation | Two upstream defects account for four failures; exact exception gate, complete report checks, frozen upstream dependencies and independent HTTP/JSON-RPC/gRPC error evidence; [diagnosis](TCK_REPORT.md) |

The [expanded implementation run](https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol/actions/runs/42438012884)
at 55fb956 passed **all 26 jobs**, including PostgreSQL and all twenty hardened-network
plans. The [main-branch workflow](https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol/actions/workflows/ci.yml?query=branch%3Amain)
records the final publication revision. Each push reruns the full matrix, including
examples/notebooks, native languages, both Compose profiles, live Ollama and TCK.

## Closure of the previous report's gaps

| Previous gap | Completed implementation | Reproducible evidence |
|---|---|---|
| Provider-native streamed tool calls | OpenAI Responses, Anthropic, Gemini and Ollama framing; safe A2A progress; complete-call schema validation | test_model_streams.py, test_model_progress.py, check_live_model.py |
| Different auth per vendor and mTLS | Bearer, API key, OAuth client credentials, OIDC and gRPC client certificates | hardened.yml, check_tls.py, check_hardened.py |
| Automated key rotation | Encrypted SQL-shared signing ring with overlap/revocation | test_auth_profiles.py, test_shared_keys.py |
| Atomic outbox and distributed rate limits | One task/event/outbox transaction, CAS revisions, leased dispatch, SQL request budgets | test_cluster.py on SQLite and PostgreSQL |
| Multi-replica delivery and reconnect chaos | Durable event journal through public SDK cluster interfaces; stream moves between handlers | test_sdk_reconnect_moves_subscription_to_another_replica |
| Complete production capstone requirements | Mixed-framework Docker network, identity, tracing, golden evaluation, durable kit, no-charge compensation, operating runbook | capstones 02/04 and deploy/HARDENED_NETWORK.md |
| Official TCK execution | Pinned unmodified upstream suite on all three bindings, raw reports, manual requirement evidence | [Detailed TCK report](TCK_REPORT.md) |
| Deeper feature practice | 108 additional full-boundary/workflow tasks beyond the prior 157, linked from lessons and feature map | validate_gym.py and [feature companion](FEATURE_DEEP_DIVES.md) |
| Files and live monitoring | Real PDF/SVG Parts, verified live webhook inbox and request metrics | module 06/17 extra examples, check_webhook_lab.py |

## Definition of done

- [x] Locked installation, no-key/no-network grading and six Python/OS combinations.
- [x] Twenty-five complete lesson structures, authored feature explanations, predictions,
  actual wire captures, quizzes, notebooks and linked graded practice.
- [x] Three bindings, all eleven operations, lifecycle, file artifacts, streaming,
  push, extensions, signatures, tenant/owner checks and protocol version handling.
- [x] Seven framework runtimes, four model providers and four native language labs.
- [x] Twenty golden scenarios, adversarial tests, failure injection and durable recovery.
- [x] Five capstone reference solutions, specific security reviews and human rubrics.
- [x] Docker network, heterogeneous authentication, TLS, Keycloak, PostgreSQL and Jaeger.
- [x] Final source and integration review; runbook for schema rollout, backup/restore,
  certificate renewal, retention and uncertain business outcomes.
- [x] Official TCK executed and its actual result retained without relabeling failures.

## External limitations, not unfinished repository code

1. **TCK:** the pinned suite reports 202 passes, 57 skips and four failures out of
   263 cases (79.6% automated requirement score). Four documented upstream
   exceptions are matched by exact class, case and complete diagnostic in the
   regression gate. Four additional real-wire controls verify the obscured protocol
   obligations; incomplete reports, extra skips and incorrect error identities fail.
   Green CI does **not** mean 100% official TCK compatibility or certification.
2. **.NET:** the official available SDK is 1.0.0-preview4. Its native lab passes;
   this repository cannot turn an upstream prerelease into a stable release.
3. **Hosted models:** OpenAI, Anthropic and Gemini are verified against provider
   framing with offline fixtures. Live account calls require the owner's account;
   only the free Ollama provider is live-tested by CI.
4. **Operating environment:** local Docker was unavailable, so Linux CI supplies
   container evidence. The local CA and loopback lab are not a hosted public service.
   Certificate operation, backups, capacity and retention remain operator duties.
5. **Design grading:** automated checks assess structure and executable behavior.
   A human must apply design/security rubrics; a passing script does not certify judgment.

Sources and compatibility decisions are in [verification notes](VERIFICATION_NOTES.md).
Use [integration commands](INTEGRATION_LABS.md), [the hardened runbook](../deploy/HARDENED_NETWORK.md)
and [the feature map](FEATURE_MAP.md) to reproduce the evidence.
