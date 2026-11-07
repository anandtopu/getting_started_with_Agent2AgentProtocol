"""Design Your Own Network: deterministic reference slice. Run from the repository root."""

import asyncio

from common.lessons import experiment
from common.pretty import show


async def main() -> None:
    show(await experiment("orchestrate"))


if __name__ == "__main__":
    asyncio.run(main())
