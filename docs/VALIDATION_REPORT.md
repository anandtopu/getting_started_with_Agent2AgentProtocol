# Validation report — 2026-11-07

Repository: [getting_started_with_Agent2AgentProtocol](https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol)

This report distinguishes runnable implementation from completeness of the larger
course brief. The repository is an initial course implementation; the remaining
scope below is not represented as finished.

## Executed checks

| Check | Evidence |
|---|---|
| Python offline tests | pytest with socket access disabled and A2A deprecations treated as errors |
| Style | Ruff lint and formatting |
| Gym | 157 tasks across 25 modules; every starter fails and every reference solution passes |
| Examples | 112 standalone commands and all 25 notebooks passed |
| Actual network | Six-agent authenticated network, signed cards, gRPC-only print service, cross-binding Concierge |
| TypeScript | Type checking and real Python-to-TypeScript quote exchange |
| Go | Native compilation and real Python-to-Go venue quote matching the Python dataset |
| Java | Official SDK 1.5.0.Final compiled; actual authentication, quote and rejection checks passed |
| .NET | Official 1.0.0-preview4 compiled; actual authentication, quote and rejection checks passed; upstream is prerelease |
| Golden cases | All 20 scenarios, including dietary interruption and conflicting counts |
| Persistence | SQLite engine/handler restart and continuation |
| Containers | Six-agent plan, PostgreSQL restart and Jaeger trace export passed in Linux CI |
| Frameworks | All seven runtimes executed; six isolated workers passed on both Windows and Linux |
| Captures | All eleven operations across JSON-RPC, HTTP+JSON and gRPC service calls |
| Links | 686 local links checked; 62 external links passed before the latest documentation additions |

The first published revision passed all nine CI jobs: Python 3.11, 3.12 and 3.13
on Ubuntu and Windows, plus local-network/TypeScript checks on Ubuntu, Windows and
macOS. [Baseline run](https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol/actions/runs/42416003303).

The [deployment and native Go run](https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol/actions/runs/42417547352)
passed all ten jobs. It includes the corrected Jaeger v3 API check.
The [framework matrix](https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol/actions/runs/42418652586)
adds twelve isolated-framework jobs, all of which passed.

## Definition of done against the requested brief

- [x] Locked installation and default offline Python tests.
- [x] Ruff lint and format checks.
- [x] Python 3.11–3.13 CI on Ubuntu and Windows at the baseline revision.
- [x] At least 120 tasks; every module has six tasks, four types and all three levels.
- [ ] Complete conformance certification: course contracts pass; official TCK is not run.
- [x] Banned API scan and A2A deprecations treated as errors.
- [x] Security-default checks for loopback, authentication, ownership, signatures, webhooks and SSRF.
- [x] Launcher start/stop for each distinct network composition on Windows, macOS and Linux.
- [x] Tier 1 needs no LLM, keys or provider imports.
- [x] Every module has the required headings, examples, captures, quiz, tests, notebook and prediction.
- [ ] Exhaustive feature coverage: introductory rows exist, but every feature is not yet taught at the requested depth.
- [x] Runnable quick-start sequence and offline first gym task.
- [ ] Full production completeness: the remaining integrations and capstones listed below are unfinished.

Gym type coverage is eight across the repository, not eight in every module.
The original 150 tasks are small contracts; seven additional tasks use real
protocol boundaries. Design checks verify structure and require human rubric review.

## Unverified or incomplete work

- Stable .NET SDK availability is external: the implemented native lab uses the official preview.
- Provider-native streamed model tool calls and live model-account access.
- Full Keycloak/OIDC/mTLS wiring, per-skill authorization, rate limiting and automated key rotation.
- Durable webhook replay/outbox storage, multi-replica event delivery and reconnect chaos tests.
- Every-vendor intermediate-state golden assertions.
- Complete production capstone requirements and an official TCK result.
- A deep bank of six distinct full-agent tasks for every individual feature.

See [verification notes](VERIFICATION_NOTES.md) for sources and API decisions,
[integration labs](INTEGRATION_LABS.md) for commands, and
[coverage map](FEATURE_MAP.md) for the implemented teaching paths.
