# 14-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice trust, signed cards and multi-tenancy at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). A matching tenant is not permission to read another caller's task.

Acceptance cases:

```json
[
  {
    "input": {
      "task": {
        "owner": "alice",
        "tenant": "maplewood"
      },
      "principal": {
        "subject": "bob",
        "tenant": "maplewood"
      }
    },
    "expected": false
  },
  {
    "input": {
      "task": {
        "owner": "alice",
        "tenant": "maplewood"
      },
      "principal": {
        "subject": "alice",
        "tenant": "maplewood"
      }
    },
    "expected": true
  },
  {
    "input": {
      "task": {
        "owner": "alice",
        "tenant": "other"
      },
      "principal": {
        "subject": "alice",
        "tenant": "maplewood"
      }
    },
    "expected": false
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 14-05, edit the copied files, then uv run gym check 14-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
