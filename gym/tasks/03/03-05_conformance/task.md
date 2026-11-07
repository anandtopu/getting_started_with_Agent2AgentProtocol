# 03-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice your first a2a server at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Introduce the task before updates and explicitly reach a final state.

Acceptance cases:

```json
[
  {
    "input": {
      "artifacts": [
        "quote"
      ]
    },
    "expected": [
      "task",
      "working",
      "quote",
      "completed"
    ]
  },
  {
    "input": {
      "artifacts": []
    },
    "expected": [
      "task",
      "working",
      "completed"
    ]
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 03-05, edit the copied files, then uv run gym check 03-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
