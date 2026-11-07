"""Retry a signed webhook after reopening its SQLite outbox and inbox.

Concepts: A2A push delivery, at-least-once transport, durable deduplication.
Spec: A2A 1.0.1 push notifications. No running agents or model.
Run: uv run python modules/19_deployment/examples/04_durable_delivery.py.
Expected: delivered 1; accepted once. Tests also simulate a lost acknowledgement.
"""

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx

from common.delivery import DeliveryStore, durable_receiver
from common.pretty import show


async def main():
    with TemporaryDirectory() as folder:
        path = Path(folder)
        outbox = DeliveryStore(path / "outbox.sqlite")
        endpoint, secret = "http://receiver.test/notifications", b"synthetic-lab-secret"
        outbox.enqueue(
            endpoint,
            {
                "task": {
                    "id": "quote",
                    "contextId": "offsite",
                    "status": {"state": "TASK_STATE_COMPLETED"},
                }
            },
        )
        outbox.close()
        # KEY IDEA: pending deliveries belong to storage, not a process's memory.
        outbox = DeliveryStore(path / "outbox.sqlite")
        inbox = DeliveryStore(path / "inbox.sqlite")
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=durable_receiver(secret, inbox))
        ) as client:
            delivered = await outbox.dispatch(client, {endpoint: secret})
        show({"delivered": delivered, "accepted_once": inbox.accepted_count() == 1})
        outbox.close()
        inbox.close()


if __name__ == "__main__":
    asyncio.run(main())
