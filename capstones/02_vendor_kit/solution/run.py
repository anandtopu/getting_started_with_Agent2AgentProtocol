"""Vendor Agent Kit: deterministic reference slice. Run from the repository root."""

import asyncio

from common.pretty import show
from common.vendor_kit import kit_lab


async def main() -> None:
    show(await kit_lab())


if __name__ == "__main__":
    asyncio.run(main())
