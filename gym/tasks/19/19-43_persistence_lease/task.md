# 19-43: Fence an expired delivery worker

Maplewood needs this persistence guarantee: Only the current lease holder may acknowledge a delivery after recovery.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Only the current lease holder may acknowledge a delivery after recovery. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 19-43, then uv run gym check 19-43.
