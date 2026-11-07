# 07-02: Repair: assemble artifact chunks by artifact id

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice streaming and push notifications at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Append only to an existing artifact with the same ID.

Acceptance cases:

```json
[
  {
    "input": [
      {
        "id": "a",
        "text": "Mic "
      },
      {
        "id": "b",
        "text": "Light"
      },
      {
        "id": "a",
        "text": "check",
        "append": true
      }
    ],
    "expected": {
      "a": "Mic check",
      "b": "Light"
    }
  },
  {
    "input": [
      {
        "id": "a",
        "text": "orphan",
        "append": true
      }
    ],
    "expected": {
      "error": "unknown artifact"
    }
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 07-02, edit the copied files, then uv run gym check 07-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
