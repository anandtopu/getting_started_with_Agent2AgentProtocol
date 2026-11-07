"""Start the real TS server and call it from Python. Explicit local-port integration."""

import os
import secrets
import shutil
import signal
import subprocess
import time

import httpx

from common.config import ROOT
from common.protocol import as_dict, request


def main() -> None:
    token = secrets.token_urlsafe(32)
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    process = subprocess.Popen(
        [npm, "run", "vendor"],
        cwd=ROOT,
        env={**os.environ, "MAPLEWOOD_TOKEN": token},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=os.name != "nt",
    )
    try:
        with httpx.Client(
            base_url="http://127.0.0.1:8304",
            timeout=2,
            headers={"Authorization": f"Bearer {token}", "A2A-Version": "1.0"},
        ) as http:
            for attempt in range(50):
                if process.poll() is not None:
                    raise RuntimeError(process.stdout.read())
                try:
                    if http.get("/.well-known/agent-card.json").status_code == 200:
                        break
                except httpx.HTTPError:
                    time.sleep(0.1)
            response = http.post("/message:send", json=as_dict(request({"guests": 40})))
            response.raise_for_status()
            task = response.json()["task"]
            assert task["status"]["state"] == "TASK_STATE_COMPLETED", task
            quote = task["artifacts"][0]["parts"][0]["data"]
            assert quote["total_cents"] == 10000 and quote["approved"] is False, quote
            print("Python to TypeScript interoperability passed: 40 badges, 10000 USD cents.")
    finally:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
        elif process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
