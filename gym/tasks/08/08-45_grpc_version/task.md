# 08-45: Read advertised gRPC protocol compatibility

Maplewood needs this grpc guarantee: Read the advertised wire version instead of using the SDK package version.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Read the advertised wire version instead of using the SDK package version. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 08-45, then uv run gym check 08-45.
