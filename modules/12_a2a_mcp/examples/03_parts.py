"""A2A and MCP together: parts.

Concepts: Choose a tool versus a remote agent, Describe bridge information loss, Keep vendor inventory internal.
Spec: https://a2a-protocol.org/v1.0.1/specification/; protobuf: https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto.
Run: uv run python modules/12_a2a_mcp/examples/03_parts.py
Agents: in-process; no separately running services. LLM: no (scripted when needed).
Expected: corresponding wire/*.result.json; IDs and timestamps vary.
"""

import asyncio

from common.lessons import experiment
from common.pretty import show


async def main() -> None:
    # KEY IDEA: observe the actual result at this protocol boundary.
    show(await experiment("parts"))


if __name__ == "__main__":
    asyncio.run(main())
