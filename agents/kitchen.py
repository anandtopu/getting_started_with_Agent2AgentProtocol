"""Saffron's internal MCP service. Run: uv run python -m agents.kitchen (stdio)."""

import json

from mcp import Client
from mcp.server import MCPServer

from common.data import load


def kitchen_server() -> MCPServer:
    kitchen = MCPServer("Saffron kitchen inventory")

    @kitchen.tool()
    def available_menu(guests: int) -> dict:
        """Return kitchen capacity and a menu; never book or purchase anything."""
        if not 1 <= guests <= 300:
            raise ValueError("Kitchen serves 1 to 300 guests.")
        return {"available": True, "capacity": 300, "menu": load("menus.json")[0]}

    return kitchen


async def check_kitchen(guests: int) -> dict:
    # Client(server) uses the SDK's in-memory transport; no mock tool invocation.
    async with Client(kitchen_server()) as client:
        result = await client.call_tool("available_menu", {"guests": guests})
    # Leave the AnyIO context before raising an application error, so callers get
    # the intended ValueError rather than a task-group ExceptionGroup.
    if result.is_error:
        raise ValueError("Kitchen could not fulfil this brief.")
    if result.structured_content is not None:
        return result.structured_content
    return json.loads(result.content[0].text)


def main() -> None:
    kitchen_server().run(transport="stdio")


if __name__ == "__main__":
    main()
