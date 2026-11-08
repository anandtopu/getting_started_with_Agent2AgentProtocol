# 04-25: Separate exchange and work-order identities

Maplewood is upgrading its client boundary. Return the three independent identities from a real exchange.

Implement async exercise(http, brief, previous). The supplied client is in-process and carries the appropriate fixture credentials unless this is an authorization attack. Read the original brief dynamically: the grader varies guest counts. Return the result described below.

## Acceptance criteria

Return the three independent identities from a real exchange. The grader performs actual SDK requests, checks resulting state, and rejects the starter. It uses no network or API keys. Read [the trusted acceptance contract](../../../../gym/boundary_checks.py) for the exact return shape; do not edit it.

## Spec

[A2A normative operations and types](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 04-25, then uv run gym check 04-25.
