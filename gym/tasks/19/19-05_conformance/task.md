# 19-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice deployment and scale at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Cap both delay and attempts; persist retry state if delivery must survive a restart.

Acceptance cases:

```json
[
  {
    "input": {
      "base_seconds": 1,
      "attempt": 2,
      "cap_seconds": 3,
      "max_attempts": 5
    },
    "expected": 3
  },
  {
    "input": {
      "base_seconds": 1,
      "attempt": 5,
      "cap_seconds": 30,
      "max_attempts": 5
    },
    "expected": null
  },
  {
    "input": {
      "base_seconds": 2,
      "attempt": 0,
      "cap_seconds": 30,
      "max_attempts": 5
    },
    "expected": 2
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 19-05, edit the copied files, then uv run gym check 19-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
