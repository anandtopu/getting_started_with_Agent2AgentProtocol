"""Check a running Compose network, PostgreSQL restart recovery and trace export."""

import json
import subprocess
import time

import httpx

from common.config import ROOT, VENDORS, url
from common.protocol import as_dict, request

COMPOSE = [
    "docker",
    "compose",
    "--env-file",
    "deploy/secrets/network.env",
    "-f",
    "deploy/docker-compose.yml",
]


def main():
    env = dict(
        line.split("=", 1)
        for line in (ROOT / "deploy/secrets/network.env").read_text().splitlines()
        if "=" in line
    )
    with httpx.Client(timeout=30, headers={"A2A-Version": "1.0"}) as http:
        for attempt in range(120):
            try:
                assert all(
                    http.get(url(vendor) + "/health", timeout=2).status_code == 200
                    for vendor in VENDORS
                )
                break
            except (httpx.HTTPError, AssertionError):
                time.sleep(1)
        else:
            raise RuntimeError("Compose network did not become ready.")
        auth = {"Authorization": "Bearer " + env["CONCIERGE_TOKEN"]}
        brief = {
            "guests": 40,
            "dietary": {"vegan": 40},
            "needs": list(VENDORS[:-1]),
            "budget_cents": 1000000,
        }
        response = http.post(
            url("concierge") + "/message:send", headers=auth, json=as_dict(request(brief))
        )
        response.raise_for_status()
        assert response.json()["task"]["status"]["state"] == "TASK_STATE_COMPLETED", response.text
        catering_auth = {"Authorization": "Bearer " + env["CATERING_TOKEN"]}
        first = http.post(
            url("catering") + "/message:send",
            headers=catering_auth,
            json=as_dict(request({"guests": 40})),
        ).json()["task"]
        assert first["status"]["state"] == "TASK_STATE_INPUT_REQUIRED"
        subprocess.run(COMPOSE + ["restart", "catering"], check=True, timeout=60)
        for attempt in range(60):
            try:
                if http.get(url("catering") + "/health", timeout=2).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        followup = request(
            {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
        )
        second = http.post(
            url("catering") + "/message:send", headers=catering_auth, json=as_dict(followup)
        ).json()["task"]
        assert second["id"] == first["id"] and second["status"]["state"] == "TASK_STATE_COMPLETED"
        for attempt in range(30):
            services = http.get("http://127.0.0.1:16686/api/services").json().get("data", [])
            if "maplewood-concierge" in services:
                break
            time.sleep(1)
        else:
            raise AssertionError("No Concierge traces reached Jaeger.")
    print(
        json.dumps(
            {"six_agent_plan": "passed", "postgres_restart": "passed", "jaeger_export": "passed"}
        )
    )


if __name__ == "__main__":
    main()
