# Legacy: migrating older agents

This is the only course guide that intentionally presents obsolete spellings.
Verify changes against the [official migration guide](https://github.com/a2aproject/a2a-python/blob/v1.3.0/docs/migrations/v1_0/README.md).

| Legacy | Current |
|---|---|
| /.well-known/agent.json | /.well-known/agent-card.json (already changed in 0.3) |
| message/send | SendMessage |
| message/stream | SendStreamingMessage |
| tasks/get | GetTask |
| tasks/cancel | CancelTask |
| tasks/resubscribe | SubscribeToTask |
| A2AStarletteApplication / A2AFastAPIApplication | Ordinary Starlette/FastAPI with route factories |
| Pydantic TextPart/FilePart/DataPart wrappers | Protobuf Part with text/raw/url/data oneof |
| supportsAuthenticatedExtendedCard | capabilities.extendedAgentCard |
| Top-level card URL and protocol version | supportedInterfaces entries |
| Lowercase role/state strings | ROLE_USER / ROLE_AGENT and TASK_STATE_* values |
| kind discriminator and status-event final flag | StreamResponse member and transport stream closure |

~~~python
# Current server composition
from fastapi import FastAPI
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes


def application(card, handler):
    return FastAPI(
        routes=[
            *create_agent_card_routes(card),
            *create_jsonrpc_routes(handler, rpc_url="/rpc"),
        ]
    )
~~~

The SDK can offer an explicitly configured compatibility interface. Keep that
interface and its tests separate from the main v1 teaching path. Compatibility
does not imply every v1 feature can be represented for an older client.

Never move authentication credentials into message parts during migration.
Keep tokens in transport headers; verify push senders at the receiver.
