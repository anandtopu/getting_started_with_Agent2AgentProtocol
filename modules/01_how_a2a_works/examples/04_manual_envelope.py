"""Inspect JSON-RPC SendMessage without an A2A SDK on the server.

Spec: A2A 1.0.1 JSON-RPC binding and Task. Run from the repository root:
uv run python modules/01_how_a2a_works/examples/04_manual_envelope.py
No running agents or model. Expected: matching RPC id, completed task, quote.
"""

import asyncio

import httpx

from common.config import ROOT
from common.manual_server import manual_app
from common.pretty import show
from common.wire import Recorder


async def main() -> None:
    transport = Recorder(httpx.ASGITransport(app=manual_app()))
    async with httpx.AsyncClient(transport=transport, base_url="http://manual.test") as client:
        response = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": "learning-1",
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
        show(response.json())
    # KEY IDEA: learner captures belong in workspace, not the committed reference.
    transport.save(ROOT / "workspace/wire/manual.jsonl")


if __name__ == "__main__":
    asyncio.run(main())
