"""Audit six planted attacks. Run: uv run python capstones/03_rogue_audit/solution/run.py."""

import asyncio

from common.audit import audit_lab
from common.pretty import show


async def main() -> None:
    show(await audit_lab())


if __name__ == "__main__":
    asyncio.run(main())
