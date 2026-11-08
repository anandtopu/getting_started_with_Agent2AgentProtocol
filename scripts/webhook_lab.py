"""Live signed callback lab, including durable outbox recovery after restart.

Run in one terminal; open the Control Room in another. Ctrl+C stops both servers.
"""

import asyncio
import json
import secrets

import httpx
import uvicorn
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from common.config import ROOT
from common.delivery import DeliveryStore, durable_receiver
from common.security import Principal
from common.vendor_kit import vendor_kit


async def main():
    folder = ROOT / "workspace/webhook-lab"
    folder.mkdir(parents=True, exist_ok=True)
    config = folder / "credentials.json"
    if not config.exists():
        config.write_text(
            json.dumps({"token": secrets.token_urlsafe(32), "secret": secrets.token_hex(32)}),
            encoding="utf-8",
        )
    settings = json.loads(config.read_text(encoding="utf-8"))
    inbox = DeliveryStore(str(folder / "inbox.sqlite"))
    endpoint = "http://127.0.0.1:8190/notifications"
    async with httpx.AsyncClient() as callback:
        async with vendor_kit(
            "sqlite+aiosqlite:///" + (folder / "tasks.sqlite").as_posix(),
            {settings["token"]: Principal("coordinator")},
            Ed25519PrivateKey.generate(),
            callback,
            {endpoint: bytes.fromhex(settings["secret"])},
            endpoint="http://127.0.0.1:8161",
        ) as (app, _):
            servers = [
                uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=port))
                for application, port in [
                    (app, 8161),
                    (durable_receiver(bytes.fromhex(settings["secret"]), inbox), 8190),
                ]
            ]
            try:
                await asyncio.gather(*(server.serve() for server in servers))
            finally:
                for server in servers:
                    server.should_exit = True
    inbox.close()


if __name__ == "__main__":
    asyncio.run(main())
