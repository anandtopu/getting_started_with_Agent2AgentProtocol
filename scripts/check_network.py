"""Exercise the supervisor's start, readiness, authenticated calls and shutdown."""

import argparse
import json
import socket
import subprocess
import sys
import time

import grpc
import httpx
from a2a.types.a2a_pb2_grpc import A2AServiceStub

from common.config import GRPC_PORT, PORTS, ROOT, grpc_target, network_members, url
from common.protocol import as_dict, request


def check_module(module: int, frameworks: bool = False) -> None:
    log = ROOT / "workspace/network-check.log"
    log.parent.mkdir(exist_ok=True)
    with log.open("w", encoding="utf-8") as handle:
        process = subprocess.Popen(
            [sys.executable, "scripts/network.py", "up", "--module", str(module)]
            + (["--frameworks"] if frameworks else []),
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.STDOUT,
        )
        try:
            state = ROOT / "workspace/network.json"
            members = network_members(module)
            with httpx.Client(timeout=1) as http:
                for attempt in range(150):
                    if process.poll() is not None:
                        raise RuntimeError("Network exited. Inspect workspace/network-check.log.")
                    ready = True
                    for vendor in members:
                        try:
                            ready &= http.get(url(vendor) + "/health").status_code == 200
                        except httpx.HTTPError:
                            ready = False
                    if ready and state.exists():
                        break
                    time.sleep(0.1)
                else:
                    raise RuntimeError("Network readiness timeout.")
                tokens = json.loads(state.read_text())["tokens"]
                for vendor in members:
                    headers = {"Authorization": "Bearer " + tokens[vendor], "A2A-Version": "1.0"}
                    payload = request(
                        {
                            "guests": 40,
                            "date": "2027-06-01",
                            "dietary": {"vegan": 40},
                            "budget_cents": 1000000,
                            "needs": ["venues", "catering", "av", "travel", "print"],
                        }
                    )
                    if vendor == "print":
                        discovered = http.get(url(vendor) + "/.well-known/agent-card.json").json()
                        assert [
                            i["protocolBinding"] for i in discovered["supportedInterfaces"]
                        ] == ["GRPC"]
                        assert http.post(url(vendor) + "/message:send", json={}).status_code == 404
                        with grpc.insecure_channel(grpc_target()) as channel:
                            stub = A2AServiceStub(channel)
                            try:
                                stub.SendMessage(payload, timeout=5)
                                raise AssertionError("gRPC accepted an unauthenticated request")
                            except grpc.RpcError as exc:
                                assert exc.code() == grpc.StatusCode.UNAUTHENTICATED
                            result = stub.SendMessage(
                                payload,
                                metadata=(
                                    ("authorization", headers["Authorization"]),
                                    ("a2a-version", "1.0"),
                                ),
                                timeout=90 if frameworks else 5,
                            )
                            assert (
                                as_dict(result)["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
                            )
                        continue
                    if module >= 4:
                        assert (
                            http.post(
                                url(vendor) + "/message:send", json=as_dict(payload)
                            ).status_code
                            == 401
                        )
                    response = http.post(
                        url(vendor) + "/message:send",
                        headers=headers,
                        json=as_dict(payload),
                        timeout=120 if frameworks else 15,
                    )
                    response.raise_for_status()
                    assert response.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED", (
                        response.text
                    )
                print(
                    f"Module {module:02}: {len(members)} local agents started and returned completed tasks."
                )
        finally:
            subprocess.run(
                [sys.executable, "scripts/network.py", "down"], cwd=ROOT, check=True, timeout=10
            )
            process.wait(timeout=15)
    assert not (ROOT / "workspace/network.json").exists()
    for port in [PORTS[vendor] for vendor in members] + ([GRPC_PORT] if "print" in members else []):
        with socket.socket() as connection:
            connection.settimeout(0.2)
            assert connection.connect_ex(("127.0.0.1", port)) != 0, (
                f"Listener {port} survived shutdown"
            )
    print("Supervisor stopped its children and removed local runtime credentials.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--module", type=int, choices=range(21), default=8)
    selection.add_argument(
        "--all", action="store_true", help="Check every core module, 00 through 20"
    )
    parser.add_argument("--frameworks", action="store_true")
    args = parser.parse_args()
    for module in range(21) if args.all else [args.module]:
        check_module(module, args.frameworks)


if __name__ == "__main__":
    main()
