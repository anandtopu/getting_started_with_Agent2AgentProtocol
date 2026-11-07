# B3-01: Validate Part oneof content

**Type:** build · **Level:** medium

Maplewood is preparing a 40-person offsite. Practice reading the specification and contributing at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). A protobuf oneof permits exactly one selected content alternative.

Acceptance cases:

```json
[
  {
    "input": {
      "text": "quote"
    },
    "expected": true
  },
  {
    "input": {
      "text": "quote",
      "data": {}
    },
    "expected": false
  },
  {
    "input": {
      "raw": "YWJj"
    },
    "expected": true
  },
  {
    "input": {
      "filename": "missing.txt"
    },
    "expected": false
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start B3-01, edit the copied files, then uv run gym check B3-01.

**Security question:** What could a malicious peer send here, and where must you reject it?
