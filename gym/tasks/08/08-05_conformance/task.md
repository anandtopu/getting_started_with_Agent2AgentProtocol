# 08-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice protocol bindings at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). HTTP routes differ from JSON-RPC method strings; protobuf annotations define the mapping.

Acceptance cases:

```json
[
  {
    "input": {
      "operation": "SendMessage"
    },
    "expected": [
      "POST",
      "/message:send"
    ]
  },
  {
    "input": {
      "operation": "GetTask",
      "id": "quote-2"
    },
    "expected": [
      "GET",
      "/tasks/quote-2"
    ]
  },
  {
    "input": {
      "operation": "CancelTask",
      "id": "quote-3"
    },
    "expected": [
      "POST",
      "/tasks/quote-3:cancel"
    ]
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 08-05, edit the copied files, then uv run gym check 08-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
