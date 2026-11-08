# 15-41: Defend a real I/O boundary: unlisted

Maplewood needs this egress guarantee: Enforce explicit destinations, public addresses, byte limits and replay protection before accepting external data.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Enforce explicit destinations, public addresses, byte limits and replay protection before accepting external data. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 15-41, then uv run gym check 15-41.
