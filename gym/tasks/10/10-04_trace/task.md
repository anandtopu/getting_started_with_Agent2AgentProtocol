# 10-04: Identify the captured transport boundaries

**Type:** trace · **Level:** medium

Maplewood is preparing a 40-person offsite. Practice the orchestrator at its vendor boundary.

## Requirements and acceptance criteria

Read trace.jsonl. In answer.json provide http_exchanges (count), grpc_service_calls (count), and http_methods (sorted unique strings). A protobuf service-boundary record is not an HTTP/2 capture. Explain which component initiated each exchange.

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 10-04, edit the copied files, then uv run gym check 10-04.

**Security question:** What could a malicious peer send here, and where must you reject it?
