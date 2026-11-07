# B2-02: Repair: select sdk releases by protocol support

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice other official sdks at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Official project membership and stable support for the target protocol are separate checks.

Acceptance cases:

```json
[
  {
    "input": [
      {
        "language": "Go",
        "protocols": [
          "1.0"
        ],
        "stable": true
      },
      {
        "language": "Java",
        "protocols": [
          "0.3"
        ],
        "stable": true
      }
    ],
    "expected": [
      "Go"
    ]
  },
  {
    "input": [
      {
        "language": ".NET",
        "protocols": [
          "1.0"
        ],
        "stable": false
      }
    ],
    "expected": []
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start B2-02, edit the copied files, then uv run gym check B2-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
