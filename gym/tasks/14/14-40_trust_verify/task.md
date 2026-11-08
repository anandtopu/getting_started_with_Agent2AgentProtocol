# 14-40: Verify a pinned vendor signature

Maplewood needs this trust guarantee: Verify cryptographic integrity before accepting the vendor identity.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Verify cryptographic integrity before accepting the vendor identity. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 14-40, then uv run gym check 14-40.
