# 10-43: Coordinate vendor work: private

Maplewood needs this orchestration guarantee: Use only provisioned vendor clients, preserve paused IDs, inspect every delegation, and require approval. The grader varies vendors, missing inputs, and failure modes.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Use only provisioned vendor clients, preserve paused IDs, inspect every delegation, and require approval. The grader varies vendors, missing inputs, and failure modes. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 10-43, then uv run gym check 10-43.
