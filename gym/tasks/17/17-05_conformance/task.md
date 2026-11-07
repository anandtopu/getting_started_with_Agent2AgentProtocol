# 17-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice observability and evaluation at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Match identity and cardinality; equal list lengths do not prove correct delegation.

Acceptance cases:

```json
[
  {
    "input": {
      "actual": [
        "venues",
        "catering"
      ],
      "expected": [
        "catering",
        "venues"
      ]
    },
    "expected": true
  },
  {
    "input": {
      "actual": [
        "venues",
        "venues"
      ],
      "expected": [
        "venues",
        "catering"
      ]
    },
    "expected": false
  },
  {
    "input": {
      "actual": [
        "venues"
      ],
      "expected": [
        "venues",
        "av"
      ]
    },
    "expected": false
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 17-05, edit the copied files, then uv run gym check 17-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
