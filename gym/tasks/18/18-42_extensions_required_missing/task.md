# 18-42: Reject an unmet required extension

Maplewood needs this extensions guarantee: Observe negotiation at the A2A request boundary; the card declaration alone does not activate an extension.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Observe negotiation at the A2A request boundary; the card declaration alone does not activate an extension. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 18-42, then uv run gym check 18-42.
