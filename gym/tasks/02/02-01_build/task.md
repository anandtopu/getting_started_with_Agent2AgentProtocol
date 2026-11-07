# 02-01: Select a compatible advertised interface

**Type:** build · **Level:** medium

Maplewood is preparing a 40-person offsite. Practice agent cards and discovery at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Respect both protocol version and binding, preserving advertised preference.

Acceptance cases:

```json
[
  {
    "input": {
      "interfaces": [
        {
          "url": "http://print",
          "protocolBinding": "GRPC",
          "protocolVersion": "1.0"
        },
        {
          "url": "http://venues",
          "protocolBinding": "JSONRPC",
          "protocolVersion": "1.0"
        }
      ],
      "supported": [
        "JSONRPC"
      ]
    },
    "expected": "http://venues"
  },
  {
    "input": {
      "interfaces": [
        {
          "url": "http://old",
          "protocolBinding": "JSONRPC",
          "protocolVersion": "0.3"
        }
      ],
      "supported": [
        "JSONRPC"
      ]
    },
    "expected": null
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 02-01, edit the copied files, then uv run gym check 02-01.

**Security question:** What could a malicious peer send here, and where must you reject it?
