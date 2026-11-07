# 14-07: Reject a forged skill description

Accept only a card whose signature verifies under the supplied pinned keys. Return a boolean.

## Acceptance criteria

The trusted grader uses actual SDK routes or protobuf calls and adversarial inputs. No ports, API keys, or model are required. Your starter must fail before the fix; your solution must pass every assertion.

## Spec

[A2A 1.0.1](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run: uv run gym start 14-07, then uv run gym check 14-07.
