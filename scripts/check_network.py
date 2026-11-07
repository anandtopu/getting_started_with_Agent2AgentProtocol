"""Exercise the supervisor's start, readiness, authenticated calls and shutdown."""

import argparse
import json
import subprocess
import sys
import time

import grpc
import httpx
from a2a.types.a2a_pb2_grpc import A2AServiceStub

from common.config import ROOT, grpc_target, network_members, url
from common.protocol import as_dict, request


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=int, default=8)
    args = parser.parse_args()
    log = ROOT / "workspace/network-check.log"
    log.parent.mkdir(exist_ok=True)
    with log.open("w", encoding="utf-8") as handle:
        process = subprocess.Popen(
            [sys.executable, "scripts/network.py", "up", "--module", str(args.module)],
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.STDOUT,
        )
        try:
            state = ROOT / "workspace/network.json"
            members = network_members(args.module)
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
                                timeout=5,
                            )
                            assert (
                                as_dict(result)["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
                            )
                        continue
                    response = http.post(
                        url(vendor) + "/message:send",
                        headers=headers,
                        json=as_dict(payload),
                        timeout=15,
                    )
                    response.raise_for_status()
                    assert response.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED", (
                        response.text
                    )
                print(
                    f"Module {args.module:02}: {len(members)} local agents started and returned completed tasks."
                )
        finally:
            subprocess.run(
                [sys.executable, "scripts/network.py", "down"], cwd=ROOT, check=True, timeout=10
            )
            process.wait(timeout=15)
    assert not (ROOT / "workspace/network.json").exists()
    print("Supervisor stopped its children and removed local runtime credentials.")


if __name__ == "__main__":
    main()
