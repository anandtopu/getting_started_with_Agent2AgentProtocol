"""Build the pinned official Go SDK agent and verify Python-to-Go interoperability."""

import os
import secrets
import subprocess
import time

import httpx

from agents.business import quote
from common.config import ROOT
from common.protocol import as_dict, request


def main():
    folder = ROOT / "modules/bonus/B2_other_sdks/go"
    binary = ROOT / "workspace" / ("granite-go.exe" if os.name == "nt" else "granite-go")
    binary.parent.mkdir(exist_ok=True)
    subprocess.run(["go", "build", "-o", str(binary), "."], cwd=folder, check=True, timeout=180)
    token = secrets.token_urlsafe(32)
    process = subprocess.Popen(
        [str(binary), "--data", str(ROOT / "data/venues.json")],
        env={**os.environ, "MAPLEWOOD_TOKEN": token},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(
            base_url="http://127.0.0.1:8400", timeout=3, headers={"A2A-Version": "1.0"}
        ) as http:
            for attempt in range(50):
                try:
                    card = http.get("/.well-known/agent-card.json")
                    if card.status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            brief = {"guests": 40, "date": "2027-06-01"}
            envelope = {
                "jsonrpc": "2.0",
                "id": "python-go",
                "method": "SendMessage",
                "params": as_dict(request(brief)),
            }
            assert http.post("/rpc", json=envelope).status_code == 401
            response = http.post(
                "/rpc", json=envelope, headers={"Authorization": "Bearer " + token}
            )
            response.raise_for_status()
            task = response.json()["result"]["task"]
            assert task["status"]["state"] == "TASK_STATE_COMPLETED", response.text
            result = task["artifacts"][0]["parts"][0]["data"]
            assert result == quote("venues", brief), result
            print("Python-to-Go quote matches the shared synthetic inventory.")
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
