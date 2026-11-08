"""Build SendMessage/GetTask without importing an A2A SDK on the server.

Concepts: JSON-RPC correlation, task identity and polling.
Spec: https://a2a-protocol.org/v1.0.1/specification/
Run: uv run python modules/03_first_server/examples/04_manual_get.py
Agents: in-process; no separate services or LLM. Expected: send.result.task
equals get.result, while the RPC response IDs are 'send' and 'get'.
"""

import asyncio
import json

import httpx

from common.manual_server import manual_app


async def main() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=manual_app()), base_url="http://manual.test"
    ) as client:
        first = (
            await client.post(
                "/rpc",
                json={
                    "jsonrpc": "2.0",
                    "id": "send",
                    "method": "SendMessage",
                    "params": {
                        "message": {
                            "messageId": "brief-1",
                            "role": "ROLE_USER",
                            "parts": [{"data": {"guests": 40}}],
                        }
                    },
                },
            )
        ).json()
        # KEY IDEA: polling uses the work ID, not the first RPC exchange ID.
        task = first["result"]["task"]
        second = (
            await client.post(
                "/rpc",
                json={
                    "jsonrpc": "2.0",
                    "id": "get",
                    "method": "GetTask",
                    "params": {"id": task["id"]},
                },
            )
        ).json()
        assert second["id"] == "get" and second["result"] == task
        print(json.dumps({"send": first, "get": second}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
