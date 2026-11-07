"""Test the explicitly labeled official .NET preview with real Python requests."""

import argparse
import json
import os
import secrets
import shutil
import subprocess
import time

import httpx

from agents.business import quote
from common.config import ROOT
from common.protocol import as_dict, request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dotnet", default=shutil.which("dotnet"))
    args = parser.parse_args()
    if not args.dotnet:
        raise SystemExit("Install .NET 10 SDK or pass --dotnet PATH.")
    folder = ROOT / "modules/bonus/B2_other_sdks/dotnet"
    subprocess.run(
        [args.dotnet, "build", "-c", "Release", "--nologo", "-p:RestoreLockedMode=true"],
        cwd=folder,
        check=True,
        timeout=180,
    )
    token = secrets.token_urlsafe(32)
    log = ROOT / "workspace/dotnet-server.log"
    log.parent.mkdir(exist_ok=True)
    records = []
    with log.open("w", encoding="utf-8") as output:
        process = subprocess.Popen(
            [args.dotnet, str(folder / "bin/Release/net10.0/Granite.dll")],
            env={
                **os.environ,
                "MAPLEWOOD_TOKEN": token,
                "MAPLEWOOD_VENUES_FILE": str(ROOT / "data/venues.json"),
            },
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            with httpx.Client(base_url="http://127.0.0.1:8402", timeout=30) as http:
                for _ in range(100):
                    if process.poll() is not None:
                        raise RuntimeError("Server exited; read workspace/dotnet-server.log.")
                    try:
                        card = http.get("/.well-known/agent-card.json")
                        if card.status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.2)
                else:
                    raise RuntimeError(".NET discovery did not become ready.")
                assert card.json()["supportedInterfaces"][0]["protocolVersion"] == "1.0"
                for guests in (40, 150, True, -1):
                    brief = {"guests": guests, "date": "2027-06-01"}
                    envelope = {
                        "jsonrpc": "2.0",
                        "id": "python-dotnet",
                        "method": "SendMessage",
                        "params": as_dict(request(brief)),
                    }
                    assert http.post("/rpc", json=envelope).status_code == 401
                    response = http.post(
                        "/rpc",
                        json=envelope,
                        headers={"Authorization": "Bearer " + token, "A2A-Version": "1.0"},
                    )
                    response.raise_for_status()
                    assert "result" in response.json(), response.text
                    records.append({"request": envelope, "response": response.json()})
                    task = response.json()["result"]["task"]
                    try:
                        expected = quote("venues", brief)
                    except ValueError:
                        assert task["status"]["state"] == "TASK_STATE_REJECTED", response.text
                    else:
                        assert task["status"]["state"] == "TASK_STATE_COMPLETED", response.text
                        assert task["artifacts"][0]["parts"][0]["data"] == expected
            (ROOT / "modules/bonus/B2_other_sdks/wire/dotnet.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in records), encoding="utf-8"
            )
            print(".NET preview: discovery, authentication, native quotes and rejection passed.")
        finally:
            process.terminate()
            process.wait(timeout=15)


if __name__ == "__main__":
    main()
