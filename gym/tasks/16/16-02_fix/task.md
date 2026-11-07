# 16-02: Repair: detect invalid mixed event streams

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice testing, conformance and debugging at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). A direct message is a complete response; a task stream needs a valid introduction and stop condition.

Acceptance cases:

```json
[
  {
    "input": [
      "message"
    ],
    "expected": true
  },
  {
    "input": [
      "message",
      "task"
    ],
    "expected": false
  },
  {
    "input": [
      "working",
      "completed"
    ],
    "expected": false
  },
  {
    "input": [
      "task",
      "working",
      "completed"
    ],
    "expected": true
  },
  {
    "input": [
      "task",
      "working"
    ],
    "expected": false
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 16-02, edit the copied files, then uv run gym check 16-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
