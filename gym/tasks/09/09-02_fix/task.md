# 09-02: Repair: validate model-selected tool names

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice putting an llm behind a server at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). A model suggests tools; application code owns the allow-list.

Acceptance cases:

```json
[
  {
    "input": {
      "tool": "quote_menu"
    },
    "expected": "quote_menu"
  },
  {
    "input": {
      "tool": "ask_dietary"
    },
    "expected": "ask_dietary"
  },
  {
    "input": {
      "tool": "send_credentials"
    },
    "expected": "reject"
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 09-02, edit the copied files, then uv run gym check 09-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
