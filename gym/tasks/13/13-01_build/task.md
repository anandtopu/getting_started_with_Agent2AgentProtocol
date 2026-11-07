# 13-01: Authorize the requested partner skill

**Type:** build · **Level:** medium

Maplewood is preparing a 40-person offsite. Practice authentication and authorization at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Authentication alone does not grant partner pricing.

Acceptance cases:

```json
[
  {
    "input": {
      "authenticated": true,
      "skill": "travel.partner_quote",
      "scopes": []
    },
    "expected": false
  },
  {
    "input": {
      "authenticated": true,
      "skill": "travel.partner_quote",
      "scopes": [
        "partner"
      ]
    },
    "expected": true
  },
  {
    "input": {
      "authenticated": false,
      "skill": "travel.quote",
      "scopes": [
        "partner"
      ]
    },
    "expected": false
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 13-01, edit the copied files, then uv run gym check 13-01.

**Security question:** What could a malicious peer send here, and where must you reject it?
