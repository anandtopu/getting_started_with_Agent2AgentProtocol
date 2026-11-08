# 19-41: Reject a stale task writer

Maplewood needs this persistence guarantee: Write once, then retry with the old version token and detect the conflict.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Write once, then retry with the old version token and detect the conflict. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 19-41, then uv run gym check 19-41.
