"""Real TLS and mutual-TLS handshakes, including missing and untrusted identities."""

import asyncio
import json
import os
import secrets
import ssl
import subprocess
import sys

import grpc
import httpx
from a2a.types.a2a_pb2_grpc import A2AServiceStub

from common.config import PORTS, ROOT
from common.protocol import as_dict, request
from deploy.certificates import generate


async def main():
    folder = ROOT / "workspace/tls-check"
    generate(folder)
    token = secrets.token_urlsafe(32)
    ca = folder / "ca.pem"
    context = ssl.create_default_context(cafile=str(ca))
    processes, logs = [], []
    try:
        for vendor in ("venues", "catering", "print"):
            log = (folder / (vendor + ".log")).open("w", encoding="utf-8")
            logs.append(log)
            env = {
                **os.environ,
                "MAPLEWOOD_TOKEN": token,
                "MAPLEWOOD_HARDENED": "1",
                "MAPLEWOOD_TLS_CERT": str(folder / (vendor + ".pem")),
                "MAPLEWOOD_TLS_KEY": str(folder / (vendor + "-key.pem")),
                "MAPLEWOOD_TLS_CA": str(ca),
                "MAPLEWOOD_VENDOR_URLS": json.dumps(
                    {v: f"https://127.0.0.1:{p}" for v, p in PORTS.items()}
                ),
            }
            processes.append(
                subprocess.Popen(
                    [sys.executable, "-m", "agents.server", "--vendor", vendor],
                    cwd=ROOT,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
            )
        async with httpx.AsyncClient(verify=context, timeout=3) as http:
            for _ in range(100):
                try:
                    statuses = [
                        await http.get(f"https://127.0.0.1:{PORTS[v]}/health")
                        for v in ("venues", "catering", "print")
                    ]
                    if all(r.status_code == 200 for r in statuses):
                        break
                except httpx.HTTPError:
                    pass
                if any(p.poll() is not None for p in processes):
                    raise RuntimeError("TLS server exited; inspect workspace/tls-check logs")
                await asyncio.sleep(0.1)
            else:
                raise RuntimeError("TLS servers not ready")
            for vendor, headers in [
                ("venues", {"Authorization": "Bearer " + token}),
                ("catering", {"X-API-Key": token}),
            ]:
                response = await http.post(
                    f"https://127.0.0.1:{PORTS[vendor]}/message:send",
                    headers={"A2A-Version": "1.0", **headers},
                    json=as_dict(request({"guests": 40, "dietary": {"vegan": 40}})),
                )
                response.raise_for_status()
                assert response.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
                tls = response.extensions["network_stream"].get_extra_info("ssl_object")
                assert tls.version() in {"TLSv1.2", "TLSv1.3"}
        async with httpx.AsyncClient(timeout=3) as untrusted:
            try:
                await untrusted.get("https://127.0.0.1:8100/health")
            except httpx.ConnectError:
                pass
            else:
                raise AssertionError("Untrusted CA was accepted")
        for with_certificate in (False, True):
            credentials = grpc.ssl_channel_credentials(
                ca.read_bytes(),
                (folder / "client-key.pem").read_bytes() if with_certificate else None,
                (folder / "client.pem").read_bytes() if with_certificate else None,
            )
            async with grpc.aio.secure_channel("127.0.0.1:8204", credentials) as channel:
                try:
                    response = await A2AServiceStub(channel).SendMessage(
                        request({"guests": 40}), metadata=(("a2a-version", "1.0"),), timeout=3
                    )
                    assert with_certificate and response.task.id
                except grpc.aio.AioRpcError:
                    if with_certificate:
                        raise
        print(
            json.dumps(
                {
                    "https": "passed",
                    "api_key": "passed",
                    "ca_validation": "passed",
                    "mutual_tls": "passed",
                }
            )
        )
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        for log in logs:
            log.close()


if __name__ == "__main__":
    asyncio.run(main())
