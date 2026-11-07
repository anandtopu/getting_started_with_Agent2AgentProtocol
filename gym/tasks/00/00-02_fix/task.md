# 00-02: Repair: select the loopback vendor url

**Type:** fix · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice setup and orientation at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Bind local teaching services to the loopback interface.

Acceptance cases:

```json
[
  {
    "input": {
      "port": 8100
    },
    "expected": "http://127.0.0.1:8100"
  },
  {
    "input": {
      "port": 8102
    },
    "expected": "http://127.0.0.1:8102"
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 00-02, edit the copied files, then uv run gym check 00-02.

**Security question:** What could a malicious peer send here, and where must you reject it?
