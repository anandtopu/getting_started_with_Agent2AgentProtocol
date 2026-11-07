# B1-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice a2a in typescript at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Compare semantic values, not generated identifiers or object implementations.

Acceptance cases:

```json
[
  {
    "input": {
      "python": {
        "total_cents": 100,
        "currency": "USD"
      },
      "typescript": {
        "total_cents": 100,
        "currency": "EUR"
      }
    },
    "expected": false
  },
  {
    "input": {
      "python": {
        "total_cents": 100,
        "currency": "USD"
      },
      "typescript": {
        "total_cents": 100,
        "currency": "USD"
      }
    },
    "expected": true
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start B1-05, edit the copied files, then uv run gym check B1-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
