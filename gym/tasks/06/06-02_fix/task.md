# 06-02: Repair: preserve binary files using protojson

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice parts and artifacts at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Binary content becomes base64 in JSON; keep the media type and filename.

Acceptance cases:

```json
[
  {
    "input": {
      "text": "floor plan",
      "media_type": "text/plain",
      "filename": "plan.txt"
    },
    "expected": {
      "raw": "Zmxvb3IgcGxhbg==",
      "mediaType": "text/plain",
      "filename": "plan.txt"
    }
  },
  {
    "input": {
      "text": "abc",
      "media_type": "application/octet-stream",
      "filename": "art.bin"
    },
    "expected": {
      "raw": "YWJj",
      "mediaType": "application/octet-stream",
      "filename": "art.bin"
    }
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 06-02, edit the copied files, then uv run gym check 06-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
