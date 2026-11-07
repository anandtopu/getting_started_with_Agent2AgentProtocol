"""Design Your Own Network: deterministic reference slice. Run from the repository root."""

import asyncio

from common.hiring import hiring_lab
from common.pretty import show


async def main() -> None:
    show(await hiring_lab())


if __name__ == "__main__":
    asyncio.run(main())
