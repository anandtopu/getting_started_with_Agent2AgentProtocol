"""Supervise local agents with portable logs. Ctrl+C or 'down' stops this supervisor's children."""

import argparse
import json
import os
import secrets
import signal
import socket
import subprocess
import sys
import threading
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from rich.console import Console

from common.card_trust import jwks
from common.config import GRPC_PORT, PORTS, ROOT, network_members
from common.security import b64

STATE = ROOT / "workspace" / "network.json"
STOP = ROOT / "workspace" / "network.stop"
console = Console()


def logs(process: subprocess.Popen, vendor: str, color: str) -> None:
    for line in process.stdout:
        console.print(f"[{vendor}] {line.rstrip()}", style=color, markup=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["up", "down", "status"])
    parser.add_argument("--module", type=int, default=0)
    parser.add_argument(
        "--llm", action="store_true", help="Use the configured model for Concierge and catering"
    )
    parser.add_argument(
        "--frameworks",
        action="store_true",
        help="Use isolated framework workers; run scripts/setup_frameworks.py first",
    )
    args = parser.parse_args()
    STATE.parent.mkdir(exist_ok=True)
    if args.action == "down":
        STOP.touch()
        print("Stop requested. The supervisor will close its own child processes.")
        return
    if args.action == "status":
        print(STATE.read_text() if STATE.exists() else "No local network is running.")
        return
    members = network_members(args.module)
    ports = [PORTS[vendor] for vendor in members]
    if "print" in members:
        ports.append(GRPC_PORT)
    for port in ports:
        try:
            with socket.socket() as check:
                check.bind(("127.0.0.1", port))
        except OSError:
            parser.error(f"Port {port} is busy. Run scripts/check_env.py or network.py down.")
    STOP.unlink(missing_ok=True)
    tokens = {vendor: secrets.token_urlsafe(32) for vendor in members}
    keys = {vendor: Ed25519PrivateKey.generate() for vendor in members}
    trust = {vendor: jwks(key.public_key(), vendor + "-v1") for vendor, key in keys.items()}
    # Credentials stay in this ignored local file so clients can authenticate.
    STATE.write_text(
        json.dumps({"module": args.module, "tokens": tokens, "trusted_keys": trust}, indent=2),
        encoding="utf-8",
    )
    if os.name != "nt":
        STATE.chmod(0o600)
    children = []
    try:
        for vendor, color in zip(members, ["cyan", "green", "yellow", "magenta", "blue", "white"]):
            env = {
                **os.environ,
                "MAPLEWOOD_TOKEN": tokens[vendor],
                "MAPLEWOOD_SIGNING_KEY": b64(keys[vendor].private_bytes_raw()),
                "MAPLEWOOD_TRUSTED_KEYS": json.dumps(trust),
                "MAPLEWOOD_VENDOR_TIMEOUT": "90" if args.frameworks else "5",
                "MAPLEWOOD_VENDOR_TOKENS": json.dumps(
                    {k: v for k, v in tokens.items() if k != "concierge"}
                ),
            }
            command = [sys.executable, "-m", "agents.server", "--vendor", vendor]
            framework_map = {
                "venues": "adk",
                "catering": "strands",
                "av": "pydantic",
                "travel": "crewai",
                "print": "beeai",
            }
            if args.frameworks and vendor in framework_map:
                command += ["--framework", framework_map[vendor]]
            if args.llm and (
                vendor == "concierge" or (vendor == "catering" and not args.frameworks)
            ):
                command += ["--llm"]
            if args.module < 4:
                command.append("--demo")
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                start_new_session=os.name != "nt",
            )
            children.append(process)
            threading.Thread(target=logs, args=(process, vendor, color), daemon=True).start()
        console.print(
            "Network starting. Ctrl+C stops all agents; use another terminal for examples."
        )
        while not STOP.exists():
            if any(child.poll() is not None for child in children):
                raise RuntimeError("An agent exited. Check the log above and scripts/check_env.py.")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Stopping the network.")
    finally:
        for child in children:
            if child.poll() is None:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(child.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                else:
                    os.killpg(child.pid, signal.SIGTERM)
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if os.name == "nt":
                    child.kill()
                else:
                    os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        STATE.unlink(missing_ok=True)
        STOP.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
