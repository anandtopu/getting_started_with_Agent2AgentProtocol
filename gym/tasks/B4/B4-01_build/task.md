# B4-01: Follow task pagination tokens

**Type:** build · **Level:** medium

Maplewood is preparing a 40-person offsite. Practice recent changes at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Use nextPageToken as the next request's pageToken; treat the token as opaque.

Acceptance cases:

```json
[
  {
    "input": {
      "nextPageToken": "opaque-2"
    },
    "expected": "opaque-2"
  },
  {
    "input": {
      "nextPageToken": ""
    },
    "expected": null
  },
  {
    "input": {
      "tasks": []
    },
    "expected": null
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start B4-01, edit the copied files, then uv run gym check B4-01.

**Security question:** What could a malicious peer send here, and where must you reject it?
