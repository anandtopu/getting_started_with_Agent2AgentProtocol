"""Use a trusted configured binding; never send credentials to a card-supplied URL."""

import os

import grpc
import httpx
from a2a.types.a2a_pb2_grpc import A2AServiceStub

from common.config import grpc_target
from common.observability import outgoing_headers
from common.protocol import as_dict
from common.tls import grpc_credentials


class GrpcRemote:
    def __init__(self, token: str):
        credentials = grpc_credentials()
        self.channel = (
            grpc.aio.secure_channel(grpc_target(), credentials)
            if credentials
            else grpc.aio.insecure_channel(grpc_target())
        )
        self.stub = A2AServiceStub(self.channel)
        self.metadata = (
            (("a2a-version", "1.0"),)
            if credentials
            else (("authorization", f"Bearer {token}"), ("a2a-version", "1.0"))
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.channel.close()

    async def send(self, message):
        try:
            result = await self.stub.SendMessage(
                message,
                metadata=self.metadata + tuple(outgoing_headers().items()),
                timeout=float(os.environ.get("MAPLEWOOD_VENDOR_TIMEOUT", "5")),
            )
        except grpc.aio.AioRpcError as exc:
            raise httpx.TransportError(f"Print vendor: {exc.code().name}") from exc
        return as_dict(result)


async def send(client, message):
    if isinstance(client, GrpcRemote):
        return await client.send(message)
    response = await client.post(
        "/message:send",
        json=as_dict(message),
        headers=outgoing_headers(),
        timeout=float(os.environ.get("MAPLEWOOD_VENDOR_TIMEOUT", "5")),
    )
    response.raise_for_status()
    return response.json()
