"""Check the hardened Compose overlay with real Keycloak, HTTPS and gRPC mTLS."""

import asyncio
import json
import os
import ssl

import grpc
import httpx
from a2a.types.a2a_pb2_grpc import A2AServiceStub

from common.card_trust import trusted_jwks
from common.config import PORTS, ROOT
from common.protocol import as_dict, request
from common.security import verify_card


async def main():
    env = dict(
        line.split("=", 1)
        for line in (ROOT / "deploy/secrets/network.env").read_text().splitlines()
        if "=" in line
    )
    folder = ROOT / "deploy/secrets/tls"
    ca = folder / "ca.pem"
    context = ssl.create_default_context(cafile=str(ca))
    async with httpx.AsyncClient(
        verify=context, timeout=180, headers={"A2A-Version": "1.0"}
    ) as http:
        for _ in range(180):
            try:
                for vendor, port in PORTS.items():
                    (
                        await http.get(f"https://localhost:{port}/health", timeout=2)
                    ).raise_for_status()
                (
                    await http.get(
                        "https://localhost:8443/realms/maplewood/.well-known/openid-configuration",
                        timeout=2,
                    )
                ).raise_for_status()
                break
            except httpx.HTTPError:
                await asyncio.sleep(1)
        else:
            raise RuntimeError("Hardened network did not become ready")
        for vendor, port in PORTS.items():
            identity = (
                await http.get(f"https://localhost:{port}/.well-known/agent-card.json")
            ).json()
            keys = (await http.get(f"https://localhost:{port}/.well-known/jwks.json")).json()
            verify_card(identity, trusted_jwks(keys))
        tokens = {}
        for vendor in ("av", "travel"):
            response = await http.post(
                "https://localhost:8443/realms/maplewood/protocol/openid-connect/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": "concierge-" + vendor,
                    "client_secret": env[vendor.upper() + "_TOKEN"],
                    "scope": "quote",
                },
            )
            response.raise_for_status()
            tokens[vendor] = response.json()["access_token"]
        brief = {
            "guests": 40,
            "dietary": {"vegan": 40},
            "needs": [v for v in PORTS if v != "concierge"],
            "budget_cents": 1000000,
        }
        # Cross-audience tokens must not authorize another vendor.
        rejected = await http.post(
            "https://localhost:8102/message:send",
            headers={"Authorization": "Bearer " + tokens["travel"]},
            json=as_dict(request(brief)),
        )
        assert rejected.status_code == 401, rejected.text
        response = await http.post(
            "https://localhost:8105/message:send",
            headers={"Authorization": "Bearer " + env["CONCIERGE_TOKEN"]},
            json=as_dict(request(brief)),
        )
        response.raise_for_status()
        assert response.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED", response.text
    credentials = grpc.ssl_channel_credentials(
        ca.read_bytes(),
        (folder / "client-key.pem").read_bytes(),
        (folder / "client.pem").read_bytes(),
    )
    async with grpc.aio.secure_channel("localhost:8204", credentials) as channel:
        assert (
            await A2AServiceStub(channel).SendMessage(
                request({"guests": 40}), metadata=(("a2a-version", "1.0"),), timeout=90
            )
        ).task.id
    print(
        json.dumps(
            {
                "encrypted_six_agent_plan": "passed",
                "keycloak_audience_isolation": "passed",
                "rotating_signed_cards": "passed",
                "mtls_print": "passed",
                "framework_profile": os.environ.get("CHECK_FRAMEWORKS", "0"),
            }
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
