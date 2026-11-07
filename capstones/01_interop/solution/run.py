"""Compare three bindings offline; --native also verifies a real TypeScript server."""

import argparse
import asyncio
import subprocess
import sys

from common.config import ROOT
from common.interop import interop_lab
from common.pretty import show


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args()
    show(await interop_lab())
    if args.native:
        await asyncio.to_thread(
            subprocess.run,
            [sys.executable, str(ROOT / "scripts/check_typescript_interop.py")],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
