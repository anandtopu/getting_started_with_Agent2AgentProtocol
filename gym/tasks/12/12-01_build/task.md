# 12-01: Choose inventory tools versus remote work

**Type:** build · **Level:** medium

Maplewood is preparing a 40-person offsite. Practice a2a and mcp together at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Internal inventory lookup is a tool; independently owned work remains an agent task.

Acceptance cases:

```json
[
  {
    "input": {
      "operation": "inventory_lookup"
    },
    "expected": "MCP"
  },
  {
    "input": {
      "operation": "vendor_quote"
    },
    "expected": "A2A"
  },
  {
    "input": {
      "operation": "hotel_task"
    },
    "expected": "A2A"
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 12-01, edit the copied files, then uv run gym check 12-01.

**Security question:** What could a malicious peer send here, and where must you reject it?
