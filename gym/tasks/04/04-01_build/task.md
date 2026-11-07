# 04-01: Classify a response payload

**Type:** build · **Level:** medium

Maplewood is preparing a 40-person offsite. Practice your first a2a client at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Inspect the response wrapper instead of assuming every reply creates a task.

Acceptance cases:

```json
[
  {
    "input": {
      "task": {
        "id": "t1"
      }
    },
    "expected": "task"
  },
  {
    "input": {
      "message": {
        "messageId": "m1"
      }
    },
    "expected": "message"
  },
  {
    "input": {
      "error": {
        "code": -32001
      }
    },
    "expected": "error"
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 04-01, edit the copied files, then uv run gym check 04-01.

**Security question:** What could a malicious peer send here, and where must you reject it?
