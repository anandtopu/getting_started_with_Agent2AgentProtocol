# 18-02: Repair: check required extension activation

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice extensions and versioning at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). A required extension must be understood and requested; optional extensions need not be active.

Acceptance cases:

```json
[
  {
    "input": {
      "extensions": [
        {
          "uri": "urn:quote:v1",
          "required": true
        }
      ],
      "requested": []
    },
    "expected": false
  },
  {
    "input": {
      "extensions": [
        {
          "uri": "urn:quote:v1",
          "required": true
        }
      ],
      "requested": [
        "urn:quote:v1"
      ]
    },
    "expected": true
  },
  {
    "input": {
      "extensions": [
        {
          "uri": "urn:quote:v1",
          "required": false
        }
      ],
      "requested": []
    },
    "expected": true
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 18-02, edit the copied files, then uv run gym check 18-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
