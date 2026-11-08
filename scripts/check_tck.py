"""Run a pinned, unmodified official TCK; retain failures and review known contradictions.

The course adds a fixture adapter, not changes to the official tests. A successful
exit means no unexpected regressions, not certification or 100% TCK compatibility.
"""

import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

import httpx

from common.config import ROOT

REVISION = "70f6f73c30208e80c889141907e094899e6e9f05"
KNOWN_FAILURES = {
    "test_error_uses_aip193_format": "TCK contradicts HTTP_JSON-SVC-001: demands application/json instead of application/a2a+json.",
    "test_must_requirement[CORE-SEND-003-grpc]": "Generic runner treats the required unsupported-media error as a failed operation.",
    "test_must_requirement[CORE-SEND-003-jsonrpc]": "Generic runner treats the required unsupported-media error as a failed operation.",
    "test_must_requirement[CORE-SEND-003-http_json]": "Generic runner treats the required unsupported-media error as a failed operation.",
}


def is_known_failure(case):
    name = case.attrib["name"]
    failure = case.find("failure")
    message = failure.attrib.get("message", "") if failure is not None else ""
    if name == "test_error_uses_aip193_format":
        return "Error Content-Type must be application/json, got: 'application/a2a+json'" in message
    return (
        name in KNOWN_FAILURES
        and "CORE-SEND-003" in message
        and "Media type application/x-unsupported-tck-type is not supported." in message
    )


def main():
    folder = ROOT / "workspace/a2a-tck"
    if not folder.exists():
        subprocess.run(
            ["git", "clone", "https://github.com/a2aproject/a2a-tck.git", str(folder)], check=True
        )
    subprocess.run(["git", "-C", str(folder), "checkout", "--detach", REVISION], check=True)
    assert not subprocess.check_output(
        ["git", "-C", str(folder), "diff", "HEAD"], text=True
    ).strip(), "TCK must remain unmodified"
    subprocess.run(["uv", "sync", "--project", str(folder), "--python", "3.13"], check=True)
    python = folder / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = {**os.environ, "PYTHONUTF8": "1"}
    subprocess.run(
        [
            str(python),
            "-m",
            "codegen.generator",
            "--target",
            "a2a-python",
            "--output",
            "sut/a2a-python",
        ],
        cwd=folder,
        env=env,
        check=True,
    )
    with (ROOT / "workspace/tck-server.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "scripts/tck_server.py"],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            for _ in range(60):
                try:
                    if (
                        httpx.get(
                            "http://127.0.0.1:9999/.well-known/agent-card.json", timeout=1
                        ).status_code
                        == 200
                    ):
                        break
                except httpx.HTTPError:
                    pass
                if process.poll() is not None:
                    raise RuntimeError("TCK fixture server exited")
                time.sleep(0.2)
            with (ROOT / "workspace/tck-results.log").open("w", encoding="utf-8") as output:
                result = subprocess.run(
                    [
                        str(python),
                        "run_tck.py",
                        "--sut-host",
                        "http://127.0.0.1:9999",
                        "--transport",
                        "all",
                        "--",
                        "-q",
                    ],
                    cwd=folder,
                    env=env,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                    timeout=600,
                )
            root = ET.parse(folder / "reports/junitreport.xml").getroot()
            failures = {
                case.attrib["name"]
                for case in root.iter("testcase")
                if case.find("failure") is not None
            }
            errors = [
                case.attrib["name"]
                for case in root.iter("testcase")
                if case.find("error") is not None
            ]
            unexpected = {
                case.attrib["name"]
                for case in root.iter("testcase")
                if case.find("failure") is not None and not is_known_failure(case)
            }
            summary = {
                "revision": REVISION,
                "upstream_exit": result.returncode,
                "unexpected_failures": sorted(unexpected),
                "counts": {
                    key: sum(int(s.attrib.get(key, 0)) for s in root.iter("testsuite"))
                    for key in ("tests", "failures", "errors", "skipped")
                },
                "errors": errors,
                "known_upstream_failures": {
                    name: KNOWN_FAILURES[name] for name in sorted(failures & KNOWN_FAILURES.keys())
                },
                "scope": "Official scenarios through the course SDK transport policies; vendor business behavior is tested separately.",
            }
            (ROOT / "workspace/tck-summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )
            print(json.dumps(summary, indent=2))
            assert not summary["unexpected_failures"] and not errors
            assert result.returncode in (0, 1) and list(root.iter("testcase")), (
                "TCK did not complete"
            )
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
