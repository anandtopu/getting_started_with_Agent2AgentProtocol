# 15-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice security threats and defenses at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). This IP check is one layer; production fetches also need allow-lists, no redirects and DNS rebinding protection.

Acceptance cases:

```json
[
  {
    "input": {
      "address": "127.0.0.1"
    },
    "expected": false
  },
  {
    "input": {
      "address": "10.1.2.3"
    },
    "expected": false
  },
  {
    "input": {
      "address": "169.254.169.254"
    },
    "expected": false
  },
  {
    "input": {
      "address": "::1"
    },
    "expected": false
  },
  {
    "input": {
      "address": "8.8.8.8"
    },
    "expected": true
  },
  {
    "input": {
      "address": "attacker.example"
    },
    "expected": false
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 15-05, edit the copied files, then uv run gym check 15-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
