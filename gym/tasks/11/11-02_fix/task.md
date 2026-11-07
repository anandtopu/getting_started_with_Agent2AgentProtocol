# 11-02: Repair: normalize framework output at the a2a boundary

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice framework integrations at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Map validated framework results into a stable quote contract; never infer spending approval.

Acceptance cases:

```json
[
  {
    "input": {
      "vendor": "catering",
      "amount": "96000"
    },
    "expected": {
      "vendor": "catering",
      "total_cents": 96000,
      "currency": "USD",
      "approved": false
    }
  },
  {
    "input": {
      "vendor": "print",
      "amount": "10000"
    },
    "expected": {
      "vendor": "print",
      "total_cents": 10000,
      "currency": "USD",
      "approved": false
    }
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 11-02, edit the copied files, then uv run gym check 11-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
