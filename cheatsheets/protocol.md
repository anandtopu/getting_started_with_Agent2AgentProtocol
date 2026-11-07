# A2A protocol at a glance

Card → interface → authenticated request → Message or Task → status and artifacts.

- Interface version: 1.0. Specification release: 1.0.1.
- Bindings: JSONRPC, HTTP+JSON, GRPC.
- Parts: text, raw, url or data; exactly one content alternative.
- States: submitted, working; interrupted input-required/auth-required; terminal completed/failed/canceled/rejected. Wire values use TASK_STATE_ prefixes.
- New task streams start with Task; direct-message streams contain one Message.
- Chunk flags concern an artifact; task state concerns the work order.
- Keep tokens in headers; validate destinations and outputs.

See the [operation table](../docs/PROTOCOL_GUIDE.md).
