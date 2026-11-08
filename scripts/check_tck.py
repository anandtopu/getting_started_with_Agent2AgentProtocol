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
from scripts.tck_evidence import verify_wire_obligations

REVISION = "70f6f73c30208e80c889141907e094899e6e9f05"
KNOWN_FAILURES = {
    "test_error_uses_aip193_format": "TCK contradicts HTTP_JSON-SVC-001: demands application/json instead of application/a2a+json.",
    "test_must_requirement[CORE-SEND-003-grpc]": "Generic runner treats the required unsupported-media error as a failed operation.",
    "test_must_requirement[CORE-SEND-003-jsonrpc]": "Generic runner treats the required unsupported-media error as a failed operation.",
    "test_must_requirement[CORE-SEND-003-http_json]": "Generic runner treats the required unsupported-media error as a failed operation.",
}
REQUIREMENT_CLASS = "tests.compatibility.core_operations.test_requirements"
ERROR_CLASS = "tests.compatibility.core_operations.test_error_handling.TestRestErrorStructure"
EXPECTED_CASES = 263
MAX_SKIPPED = 57


def expected_failure(name):
    """The complete diagnostic at the pinned revision, not a permissive substring."""
    if name == "test_error_uses_aip193_format":
        return ERROR_CLASS, (
            "AssertionError: HTTP_JSON-ERR-001 [Error responses use google.rpc.Status JSON "
            "representation] failed on http_json: Error Content-Type must be application/json, "
            "got: 'application/a2a+json' (see specification/specification.md#116-error-handling)"
        )
    if name not in KNOWN_FAILURES:
        return None, None
    transport = name.removesuffix("]").rsplit("-", 1)[1]
    error = (
        "Operation failed: "
        + ("[400] " if transport == "http_json" else "")
        + "Media type application/x-unsupported-tck-type is not supported. "
        "Supported input modes: application/json, application/octet-stream, text/plain"
    )
    return REQUIREMENT_CLASS, (
        "AssertionError: CORE-SEND-003 [SendMessage returns ContentTypeNotSupportedError "
        f"for unsupported media] failed on {transport}: {error} "
        f"(see specification/specification.md#311-send-message)\nassert not {[error]!r}"
    )


def is_known_failure(case):
    classname, message = expected_failure(case.attrib["name"])
    failures = case.findall("failure")
    return (
        classname is not None
        and case.attrib.get("classname") == classname
        and len(failures) == 1
        and case.find("error") is None
        and case.find("skipped") is None
        and failures[0].attrib.get("message") == message
    )


def report_problems(root, returncode):
    """Fail closed on partial, duplicated, inconsistent or newly failing runs."""
    cases = list(root.iter("testcase"))
    identities = [(c.attrib.get("classname"), c.attrib.get("name")) for c in cases]
    problems = []
    if len(cases) != EXPECTED_CASES or len(set(identities)) != len(cases):
        problems.append("Incomplete or duplicated pinned TCK case inventory")
    actual = {
        "tests": len(cases),
        **{
            tag: sum(c.find(element) is not None for c in cases)
            for tag, element in (
                ("failures", "failure"),
                ("errors", "error"),
                ("skipped", "skipped"),
            )
        },
    }
    reported = {
        key: sum(int(s.attrib.get(key, 0)) for s in root.iter("testsuite")) for key in actual
    }
    if actual != reported:
        problems.append("JUnit counters do not match individual cases")
    if actual["skipped"] > MAX_SKIPPED:
        problems.append("Additional TCK cases were skipped")
    if actual["errors"] or returncode != (1 if actual["failures"] else 0):
        problems.append("TCK infrastructure error or inconsistent exit status")
    for name in KNOWN_FAILURES:
        classname, _ = expected_failure(name)
        matching = [
            c
            for c in cases
            if (c.attrib.get("classname"), c.attrib.get("name")) == (classname, name)
        ]
        if len(matching) != 1 or matching[0].find("skipped") is not None:
            problems.append(f"Required exception obligation did not execute: {name}")
    for case in cases:
        if case.find("failure") is not None and not is_known_failure(case):
            problems.append(
                f"Unexpected failure: {case.attrib.get('classname')}.{case.attrib.get('name')}"
            )
    return problems


def wait_for_fixture(process):
    with httpx.Client(timeout=1, trust_env=False) as http:
        for _ in range(60):
            if process.poll() is not None:
                raise RuntimeError("TCK fixture server exited")
            try:
                response = http.get("http://127.0.0.1:9999/.well-known/agent-card.json")
                if (
                    response.status_code == 200
                    and response.json().get("name") == "Maplewood protocol conformance fixture"
                ):
                    return
            except (httpx.HTTPError, ValueError):
                pass
            time.sleep(0.2)
    raise RuntimeError("TCK fixture server did not become ready")


def main():
    folder = ROOT / "workspace/a2a-tck"
    # Clear this run's generated evidence before setup can fail.
    report = folder / "reports/junitreport.xml"
    report.unlink(missing_ok=True)
    for filename in ("tck-summary.json", "tck-wire-evidence.json"):
        (ROOT / "workspace" / filename).unlink(missing_ok=True)
    if not folder.exists():
        subprocess.run(
            ["git", "clone", "https://github.com/a2aproject/a2a-tck.git", str(folder)], check=True
        )
    subprocess.run(["git", "-C", str(folder), "checkout", "--detach", REVISION], check=True)
    assert not subprocess.check_output(
        ["git", "-C", str(folder), "diff", "HEAD"], text=True
    ).strip(), "TCK must remain unmodified"
    subprocess.run(
        # Upstream's lock omits pyproject's <3.15 bound. Both allow 3.13;
        # --frozen installs that exact committed lock without rewriting metadata.
        ["uv", "sync", "--frozen", "--project", str(folder), "--python", "3.13"],
        check=True,
    )
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
            wait_for_fixture(process)
            evidence = verify_wire_obligations()
            (ROOT / "workspace/tck-wire-evidence.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
            )
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
            subprocess.run(["git", "-C", str(folder), "diff", "--exit-code", "HEAD"], check=True)
            root = ET.parse(report).getroot()
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
                "gate_problems": report_problems(root, result.returncode),
                "independent_wire_checks": sorted(evidence),
                "known_upstream_failures": {
                    name: KNOWN_FAILURES[name] for name in sorted(failures & KNOWN_FAILURES.keys())
                },
                "scope": "Official scenarios through the course SDK transport policies; vendor business behavior is tested separately.",
            }
            (ROOT / "workspace/tck-summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )
            print(json.dumps(summary, indent=2))
            assert not summary["gate_problems"], "TCK regression gate failed"
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
