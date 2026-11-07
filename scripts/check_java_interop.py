"""Compile the official Java SDK vendor and compare actual requests with Python."""

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
    folder = ROOT / "modules/bonus/B2_other_sdks/java"
    maven = shutil.which("mvn")
    if not maven:
        raise SystemExit("Install Maven and Java 17+; see the B2 language lab README.")
    subprocess.run([maven, "-B", "-q", "package"], cwd=folder, check=True, timeout=600)
    token = secrets.token_urlsafe(32)
    log = ROOT / "workspace/java-server.log"
    log.parent.mkdir(exist_ok=True)
    records = []
    with log.open("w", encoding="utf-8") as output:
        process = subprocess.Popen(
            ["java", "-jar", str(folder / "target/quarkus-app/quarkus-run.jar")],
            env={
                **os.environ,
                "MAPLEWOOD_TOKEN": token,
                "MAPLEWOOD_VENUES_FILE": str(ROOT / "data/venues.json"),
            },
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            with httpx.Client(base_url="http://127.0.0.1:8401", timeout=30) as http:
                for _ in range(150):
                    if process.poll() is not None:
                        raise RuntimeError("Java server exited; read workspace/java-server.log")
                    try:
                        card = http.get("/.well-known/agent-card.json")
                        if card.status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.2)
                else:
                    raise RuntimeError("Java discovery failed; read workspace/java-server.log")
                assert card.json()["supportedInterfaces"][0]["protocolVersion"] == "1.0"
                for guests in (40, 150, True, -1):
                    brief = {"guests": guests, "date": "2027-06-01"}
                    envelope = {
                        "jsonrpc": "2.0",
                        "id": "python-java",
                        "method": "SendMessage",
                        "params": as_dict(request(brief)),
                    }
                    assert http.post("/", json=envelope).status_code == 401
                    response = http.post(
                        "/",
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
            (ROOT / "modules/bonus/B2_other_sdks/wire/java.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in records), encoding="utf-8"
            )
            print(
                "Native Java SDK: discovery, authentication, quotes and invalid-input checks passed."
            )
        finally:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                process.terminate()
            process.wait(timeout=15)


if __name__ == "__main__":
    main()
