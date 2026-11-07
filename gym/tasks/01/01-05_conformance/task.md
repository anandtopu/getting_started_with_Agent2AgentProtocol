# 01-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice how a2a works at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). The method parameters contain a message object, not its individual fields.

Acceptance cases:

```json
[
  {
    "input": {
      "id": 1,
      "message": {
        "messageId": "m1",
        "role": "ROLE_USER",
        "parts": [
          {
            "text": "Quote a venue"
          }
        ]
      }
    },
    "expected": {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "SendMessage",
      "params": {
        "message": {
          "messageId": "m1",
          "role": "ROLE_USER",
          "parts": [
            {
              "text": "Quote a venue"
            }
          ]
        }
      }
    }
  },
  {
    "input": {
      "id": "m2",
      "message": {
        "messageId": "m2",
        "role": "ROLE_USER",
        "parts": [
          {
            "text": "Hold a date"
          }
        ]
      }
    },
    "expected": {
      "jsonrpc": "2.0",
      "id": "m2",
      "method": "SendMessage",
      "params": {
        "message": {
          "messageId": "m2",
          "role": "ROLE_USER",
          "parts": [
            {
              "text": "Hold a date"
            }
          ]
        }
      }
    }
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 01-05, edit the copied files, then uv run gym check 01-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
