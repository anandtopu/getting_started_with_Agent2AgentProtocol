# 09-03: Predict the first experiment's observable result

**Type:** predict · **Level:** easy

Maplewood is preparing a 40-person offsite. Practice putting an llm behind a server at its vendor boundary.

## Requirements and acceptance criteria

Predict example 01 before running it. In answer.json omit generated IDs, timestamps, signatures, tracing IDs, attributes and nextPageToken. Keep every other field and array order.

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 09-03, edit the copied files, then uv run gym check 09-03.

**Security question:** What could a malicious peer send here, and where must you reject it?
