# 14-42: Reject a self-appointed signing key

Maplewood needs this trust guarantee: Return whether the supplied card is valid under the operator's pinned keys. The fixture attacks this trust boundary.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Return whether the supplied card is valid under the operator's pinned keys. The fixture attacks this trust boundary. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 14-42, then uv run gym check 14-42.
