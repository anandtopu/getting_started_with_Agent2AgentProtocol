# Maplewood Concierge — the complete network

As a planner, I can send one brief to five independently implemented vendors, supply
missing dietary counts later, and review a combined quote. As an operator, I can
trace calls, verify identities, restart replicas, recover notifications, and detect
failed compensation without spending money automatically.

The offline reference uses a scripted model and real LangGraph/MCP execution. The
final Docker deployment uses ADK, Strands, Pydantic AI, CrewAI and BeeAI vendors,
with an optional live-model Concierge. The same A2A adapter preserves lifecycle,
files and AV chunks across implementations. Microsoft Agent Framework is also
verified in the isolated adapter matrix.

~~~mermaid
flowchart LR
    U[Planner] --> C[Concierge]
    C -->|Bearer HTTPS| V[ADK venues]
    C -->|API key HTTPS| S[Strands catering]
    C -->|OAuth HTTPS| A[Pydantic AV]
    C -->|OIDC HTTPS| T[CrewAI travel]
    C -->|mTLS gRPC| P[BeeAI print]
    V & S & A & T & P --> D[(PostgreSQL tasks and journals)]
    C & V & S & A & T & P --> J[Jaeger traces]
    C --> R[Validated plan awaiting human approval]
~~~

## Run

~~~console
uv run python capstones/04_concierge/starter/run.py
uv run python capstones/04_concierge/solution/run.py
uv run pytest capstones/04_concierge/tests tests/test_golden.py tests/test_reservations.py tests/test_cluster.py tests/test_observability.py
~~~

Follow the [hardened deployment commands](../../deploy/HARDENED_NETWORK.md) to run
the full Docker network. `scripts/check_hardened.py` verifies all twenty golden
plans through that network, including exact delegated outcomes and quotes.
For optional live planning follow [the provider guide](../../docs/LIVE_MODELS.md).

## Acceptance criteria

- Discover and verify each vendor before sending its independently provisioned credential.
- Bound model selection to configured skill IDs and send only required event fields.
- Delegate in parallel, validate quote schemas, and preserve every remote task/context mapping.
- Resume interrupted work without consulting the model again or repeating completed quotes.
- Exercise completed, rejected, failed, input-required and auth-required states;
  cancellation is a protocol operation, not compensation for completed effects.
- Test SSE chunks, snapshot/reconnect on another replica, atomic outbox rollback,
  lost acknowledgement, expired worker leases and durable receiver deduplication.
- Verify the twenty committed golden scenarios and retain raw conformance evidence.
- Deploy PostgreSQL, Keycloak and Jaeger with TLS and distinct vendor auth schemes.
- Link traces across HTTP/gRPC and correlate task/context IDs without logging credentials.
- Preserve approval_required and charged_cents=0. Optional tentative_holds uses a stable
  hold_request_id, expires after fifteen minutes, and compensates uncertain venue/hotel work.

## Filled-in security review

| Boundary | Verified control | Evidence |
|---|---|---|
| Planner to Concierge | Bearer authentication and tenant ownership | security and cluster tests |
| Concierge to vendors | Five schemes; no forwarded user token; cross-audience rejection | hardened checker |
| Discovery | Trusted HTTPS JWKS, encrypted shared rotation ring, revocation | shared-key tests |
| Model and artifacts | Bounded selection and JSON Schema validation | model-stream/planning tests |
| File and callback I/O | Exact allow-list, byte bounds, no redirects, verified sender | security and delivery tests |
| Persistence | CAS updates, transaction rollback, replica reconnect, leased outbox | cluster tests on SQLite/PostgreSQL |
| Business effects | Idempotent no-charge holds, compensation, explicit manual follow-up | reservation and compensation tests |
| Telemetry | W3C propagation, task/context attributes, credential redaction | observability tests and Jaeger check |

The [runbook](../../deploy/HARDENED_NETWORK.md) specifies renewal, recovery, retention
and schema rollout. The local teaching CA and loopback exposure are deliberate;
public deployment requires operator-owned certificates and access policies.

## Rubric

Score five areas 0–2: protocol/state fidelity, orchestration correctness, security,
failure recovery and operational evidence. Require 9/10 and no zero. For full marks,
show an interrupted task recovering on another handler, an uncertain hold being
released, and an actual distributed trace. The [TCK report](../../docs/TCK_REPORT.md)
keeps four upstream contradictions visible; do not claim external certification.

## Extend it

Add a new vendor with a reviewed skill contract, certificate identity and delegation
policy. Supply golden and adversarial scenarios before allowing real financial effects.
