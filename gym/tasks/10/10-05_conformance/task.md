# 10-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice the orchestrator at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Pass only the business fields required by the selected vendor.

Acceptance cases:

```json
[
  {
    "input": {
      "guests": 40,
      "date": "2027-06-01",
      "authorization": "secret"
    },
    "expected": {
      "guests": 40,
      "date": "2027-06-01"
    }
  },
  {
    "input": {
      "rooms": 10,
      "private_notes": "sensitive",
      "user_email": "fictional@example.invalid"
    },
    "expected": {
      "rooms": 10
    }
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 10-05, edit the copied files, then uv run gym check 10-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
