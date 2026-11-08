# 03-41: Inspect the hand-built server: get

Maplewood needs this manual guarantee: Send the supplied get envelope and return the server's response. Explain RPC failures versus business rejection.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Send the supplied get envelope and return the server's response. Explain RPC failures versus business rejection. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 03-41, then uv run gym check 03-41.
