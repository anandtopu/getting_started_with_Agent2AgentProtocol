"""Render captured operations into a readable, reproducible protocol reference."""

import json

from common.config import ROOT

EXPLANATIONS = {
    "SendMessage": "Hand a vendor a brief. The result can be a Message or a tracked Task; do not assume every response has artifacts.",
    "SendStreamingMessage": "Open a stream of task snapshots, status updates and artifact updates. Read the wrapper member to identify each event.",
    "GetTask": "Read a work order by its server-assigned ID. Ownership checks still apply; knowing an ID does not grant access.",
    "ListTasks": "Read a page of work orders. Treat nextPageToken as opaque, and preserve the filter choices for the next request.",
    "CancelTask": "Ask a vendor to stop unfinished work. This does not undo a completed reservation or payment.",
    "SubscribeToTask": "Reconnect to active work. This capture intentionally attempts a terminal task and records the real unsupported-operation error.",
    "CreateTaskPushNotificationConfig": "Register a callback destination for one task. The server checks its destination policy before accepting it.",
    "GetTaskPushNotificationConfig": "Read one callback registration using both task and configuration IDs.",
    "ListTaskPushNotificationConfigs": "Inspect all callback registrations for a task, subject to the same task-owner authorization.",
    "DeleteTaskPushNotificationConfig": "Remove a callback registration. A successful empty response does not mean the task itself was canceled.",
    "GetExtendedAgentCard": "Request an authenticated partner view. A public card does not automatically authorize this operation.",
}


def main():
    rpc = [
        json.loads(line)
        for line in (ROOT / "docs/wire/jsonrpc-operations.jsonl").read_text().splitlines()
    ]
    rest = [
        json.loads(line)
        for line in (ROOT / "docs/wire/http_json-operations.jsonl").read_text().splitlines()
    ]
    lines = [
        "# Every operation on the wire",
        "",
        "These are captured SDK 1.3.0 exchanges targeting A2A 1.0.1. Generated IDs vary.",
        "Regenerate with uv run python scripts/capture_operations.py and then this script.",
        "Credentials were redacted before writing. gRPC captures are protobuf service calls,",
        "not HTTP/2 packet captures. The live gRPC network is tested separately.",
        "",
        "[JSON-RPC records](wire/jsonrpc-operations.jsonl) · [HTTP+JSON records](wire/http_json-operations.jsonl) · [gRPC records](wire/grpc-operations.jsonl)",
        "",
    ]
    for rpc_row, rest_row in zip(rpc, rest):
        name = rpc_row["request"]["body"]["method"]
        lines += [
            "## " + name,
            "",
            EXPLANATIONS[name],
            "",
            "[Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)",
            "",
            "HTTP+JSON: " + rest_row["request"]["method"] + " " + rest_row["request"]["url"],
            "",
            "JSON-RPC request:",
            "~~~json",
            json.dumps(rpc_row["request"]["body"], indent=2),
            "~~~",
            "",
            "Actual response:",
            "~~~json",
            json.dumps(rpc_row["response"]["body"], indent=2),
            "~~~",
            "",
        ]
    (ROOT / "docs/OPERATIONS_ON_THE_WIRE.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
