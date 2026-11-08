"""Start the live callback lab, verify signed delivery, restart, and check durable state."""

import json
import sqlite3
import subprocess
import sys
import time

import httpx

from common.config import ROOT
from common.protocol import as_dict, request


def main():
    folder = ROOT / "workspace/webhook-lab"
    processes = []
    log_path = ROOT / "workspace/webhook-lab-check.log"
    log_path.parent.mkdir(exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:

        def start():
            process = subprocess.Popen(
                [sys.executable, "scripts/webhook_lab.py"], stdout=log, stderr=subprocess.STDOUT
            )
            processes.append(process)
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError("Callback lab exited; inspect its log")
                try:
                    if httpx.get("http://127.0.0.1:8161/health", timeout=1).status_code == 200:
                        return process
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            raise TimeoutError("Callback lab startup timed out")

        def stop(process):
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

        try:
            first = start()
            token = json.loads((folder / "credentials.json").read_text())["token"]
            payload = as_dict(request({"guests": 40, "dietary": {"vegan": 40}}))
            payload["configuration"] = {
                "taskPushNotificationConfig": {
                    "id": "check",
                    "url": "http://127.0.0.1:8190/notifications",
                }
            }
            response = httpx.post(
                "http://127.0.0.1:8161/message:send",
                json=payload,
                headers={"Authorization": "Bearer " + token, "A2A-Version": "1.0"},
                timeout=20,
            )
            response.raise_for_status()
            task = response.json()["task"]
            assert task["status"]["state"] == "TASK_STATE_COMPLETED"
            assert (
                httpx.post("http://127.0.0.1:8190/notifications", json={"task": task}).status_code
                == 401
            )
            for _ in range(50):
                with sqlite3.connect(folder / "inbox.sqlite") as database:
                    bodies = [
                        json.loads(row[0]) for row in database.execute("SELECT body FROM inbox")
                    ]
                if any(
                    b.get("statusUpdate", {}).get("taskId") == task["id"]
                    and b["statusUpdate"]["status"]["state"] == "TASK_STATE_COMPLETED"
                    for b in bodies
                ):
                    break
                time.sleep(0.1)
            else:
                raise AssertionError("Verified terminal callback did not arrive")
            stop(first)
            start()
            result = httpx.get(
                "http://127.0.0.1:8161/tasks/" + task["id"],
                headers={"Authorization": "Bearer " + token, "A2A-Version": "1.0"},
            )
            result.raise_for_status()
            assert result.json()["id"] == task["id"]
            with sqlite3.connect(folder / "inbox.sqlite") as database:
                assert database.execute("SELECT count(*) FROM inbox").fetchone()[0] >= len(bodies)
            print("Live signed callbacks, unsigned rejection, task and inbox restart: passed.")
        finally:
            for process in processes:
                if process.poll() is None:
                    stop(process)


if __name__ == "__main__":
    main()
