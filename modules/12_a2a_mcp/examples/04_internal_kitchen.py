"""Observe A2A outside and MCP inside Saffron.

Concepts: protocol boundaries, MCP tools and A2A tasks.
Spec: https://a2a-protocol.org/latest/specification/
Run: uv run python modules/12_a2a_mcp/examples/04_internal_kitchen.py
No agents, ports, keys or LLM needed. Expected: TASK_STATE_COMPLETED, a catering quote.
"""

import asyncio

from agents.app import make_handler
from agents.mcp_executor import KitchenExecutor
from common.pretty import show
from common.protocol import as_dict, request
from common.testing import client


async def main() -> None:
    handler = make_handler("catering", executor=KitchenExecutor())
    async with client("catering", handler=handler) as http:
        # KEY IDEA: no MCP tool names or kitchen credentials cross the A2A boundary.
        response = await http.post(
            "/message:send", json=as_dict(request({"guests": 40, "dietary": {"vegan": 40}}))
        )
        show(response.json())


if __name__ == "__main__":
    asyncio.run(main())
