# 09-43: Validate native tool frames: gemini

Maplewood needs this native_model guarantee: Consume actual provider framing, validate the final tool name and argument schema, and reject incomplete or unsafe output.

Implement async exercise(context). The trusted grader supplies real SDK clients, signing keys or independent SQL connections as appropriate. Inspect [the fixture contract](../../../../gym/advanced_checks.py) for its exact context and return shape.

## Acceptance criteria

Consume actual provider framing, validate the final tool name and argument schema, and reject incomplete or unsafe output. No network, provider keys or Docker are used. The broken starter fails; a correct solution passes the actual boundary checks.

## Spec

[A2A normative contract](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

Run uv run gym start 09-43, then uv run gym check 09-43.
