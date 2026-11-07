"""Plan with five agents, pause for dietary input, then resume without repeating quotes."""

import asyncio

from common.capstone_network import network_lab
from common.pretty import show


async def main() -> None:
    show(await network_lab())


if __name__ == "__main__":
    asyncio.run(main())
