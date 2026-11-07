"""A lost acknowledgement and process restarts must not duplicate accepted work."""

import httpx

from common.delivery import DeliveryStore, durable_receiver
from common.security import webhook_headers


async def test_acknowledgement_loss_and_restart(tmp_path):
    sender_path, receiver_path = tmp_path / "sender.sqlite", tmp_path / "receiver.sqlite"
    sender, sink = DeliveryStore(sender_path), DeliveryStore(receiver_path)
    endpoint, secret = "http://receiver.test/notifications", b"synthetic-secret"
    event = {
        "task": {
            "id": "task-1",
            "contextId": "event-1",
            "status": {"state": "TASK_STATE_COMPLETED"},
        }
    }
    sender.enqueue(endpoint, event)
    app = durable_receiver(secret, sink)

    class LostAcknowledgement(httpx.ASGITransport):
        async def handle_async_request(self, request):
            await super().handle_async_request(request)
            raise httpx.ReadError("Synthetic acknowledgement loss")

    async with httpx.AsyncClient(transport=LostAcknowledgement(app=app)) as client:
        assert await sender.dispatch(client, {endpoint: secret}, now=1000) == 0
    assert sink.accepted_count() == 1
    sender.close()
    sink.close()
    sender, sink = DeliveryStore(sender_path), DeliveryStore(receiver_path)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=durable_receiver(secret, sink))
    ) as client:
        assert await sender.dispatch(client, {endpoint: secret}, now=1002) == 1
        assert await sender.dispatch(client, {endpoint: secret}, now=1004) == 0
    assert sink.accepted_count() == 1
    sender.close()
    sink.close()


async def test_same_nonce_different_body_is_rejected(tmp_path):
    store = DeliveryStore(tmp_path / "inbox.sqlite")
    secret, body = b"synthetic-secret", b'{"task":{"id":"one"}}'
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=durable_receiver(secret, store)),
        base_url="http://receiver.test",
    ) as client:
        first = await client.post(
            "/notifications", content=body, headers=webhook_headers(body, secret, "delivery-1")
        )
        assert first.status_code == 200
        different = b'{"task":{"id":"two"}}'
        second = await client.post(
            "/notifications",
            content=different,
            headers=webhook_headers(different, secret, "delivery-1"),
        )
        assert second.status_code == 401
    assert store.accepted_count() == 1
    store.close()
