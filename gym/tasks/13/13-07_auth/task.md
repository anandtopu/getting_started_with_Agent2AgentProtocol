# 13-07: Close Granite's anonymous quote endpoint

Build a server from the supplied token-to-principal map. Reject anonymous calls and isolate task owners.

## Acceptance criteria

The trusted grader uses actual SDK routes or protobuf calls and adversarial inputs. No ports, API keys, or model are required. Your starter must fail before the fix; your solution must pass every assertion.

## Spec

[A2A 1.0.1](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run: uv run gym start 13-07, then uv run gym check 13-07.
