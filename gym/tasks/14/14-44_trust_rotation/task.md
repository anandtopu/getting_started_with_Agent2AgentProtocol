# 14-44: Keep valid keys during rotation overlap

Maplewood needs this trust guarantee: Accept the old signature during overlap and reject it after retirement.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Accept the old signature during overlap and reject it after retirement. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 14-44, then uv run gym check 14-44.
