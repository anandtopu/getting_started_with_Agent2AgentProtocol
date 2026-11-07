# 20-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice designing agent networks at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Compensation is an explicit business action, normally reversing successfully completed steps.

Acceptance cases:

```json
[
  {
    "input": {
      "failed": true,
      "holds": [
        {
          "id": "hotel",
          "confirmed": true
        },
        {
          "id": "venue",
          "confirmed": false
        }
      ]
    },
    "expected": [
      "release:hotel"
    ]
  },
  {
    "input": {
      "failed": false,
      "holds": [
        {
          "id": "hotel",
          "confirmed": true
        }
      ]
    },
    "expected": []
  },
  {
    "input": {
      "failed": true,
      "holds": [
        {
          "id": "hotel",
          "confirmed": true
        },
        {
          "id": "print",
          "confirmed": true
        }
      ]
    },
    "expected": [
      "release:print",
      "release:hotel"
    ]
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 20-05, edit the copied files, then uv run gym check 20-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
