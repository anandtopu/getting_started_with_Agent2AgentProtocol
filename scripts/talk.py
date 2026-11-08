"""Discover and message a running vendor. Run: uv run python scripts/talk.py venues."""

import argparse
import asyncio
import json

import httpx

from common.config import ROOT, VENDORS, url
from common.pretty import show
from common.protocol import as_dict, request
from common.remote import GrpcRemote


async def talk(vendor: str) -> None:
    state = ROOT / "workspace" / "network.json"
    token = json.loads(state.read_text())["tokens"].get(vendor, "") if state.exists() else ""
    try:
        async with httpx.AsyncClient(
            base_url=url(vendor),
            timeout=10,
            headers={"Authorization": f"Bearer {token}", "A2A-Version": "1.0"},
        ) as client:
            show((await client.get("/.well-known/agent-card.json")).json())
            if vendor == "print":
                async with GrpcRemote(token) as remote:
                    show(await remote.send(request({"guests": 40})))
                return
            show(
                (
                    await client.post(
                        "/message:send", json=as_dict(request({"guests": 40, "date": "2027-06-01"}))
                    )
                ).json()
            )
    except httpx.HTTPError:
        print(
            "Agent unavailable. Run uv run python scripts/network.py up --module 00 in another terminal."
        )
        raise SystemExit(1) from None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vendor", choices=VENDORS, default="venues", nargs="?")
    asyncio.run(talk(parser.parse_args().vendor))


if __name__ == "__main__":
    main()
