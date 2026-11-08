"""Build the minimal SendMessage/GetTask exchange without importing an A2A SDK."""

import asyncio
import json

import httpx

from common.manual_server import manual_app


async def main():
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
