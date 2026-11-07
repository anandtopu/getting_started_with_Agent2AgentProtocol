# 05-05: Enforce the contract across edge cases

**Type:** conformance · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice the task lifecycle in depth at its vendor boundary.

## Requirements and acceptance criteria

Implement solve(payload). Input-required and auth-required are resumable; terminal states are not.

Acceptance cases:

```json
[
  {
    "input": {
      "state": "TASK_STATE_COMPLETED"
    },
    "expected": true
  },
  {
    "input": {
      "state": "TASK_STATE_FAILED"
    },
    "expected": true
  },
  {
    "input": {
      "state": "TASK_STATE_CANCELED"
    },
    "expected": true
  },
  {
    "input": {
      "state": "TASK_STATE_REJECTED"
    },
    "expected": true
  },
  {
    "input": {
      "state": "TASK_STATE_INPUT_REQUIRED"
    },
    "expected": false
  },
  {
    "input": {
      "state": "TASK_STATE_AUTH_REQUIRED"
    },
    "expected": false
  },
  {
    "input": {
      "state": "TASK_STATE_SUBMITTED"
    },
    "expected": false
  },
  {
    "input": {
      "state": "TASK_STATE_WORKING"
    },
    "expected": false
  },
  {
    "input": {
      "state": "TASK_STATE_UNSPECIFIED"
    },
    "expected": false
  }
]
```

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 05-05, edit the copied files, then uv run gym check 05-05.

**Security question:** What could a malicious peer send here, and where must you reject it?
