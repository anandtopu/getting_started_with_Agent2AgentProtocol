"""Run a dependency-isolated framework behind the course's official A2A v1 SDK."""

import asyncio
import json
import os

from common.config import ROOT

FRAMEWORKS = ("adk", "strands", "pydantic", "crewai", "microsoft", "beeai")


async def framework_quote(framework: str, vendor: str, brief: dict, *, partner=False) -> dict:
    if framework not in FRAMEWORKS:
        raise ValueError("Unknown framework")
    folder = ROOT / "integrations" / framework / ".venv"
    python = folder / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        raise ValueError(
            f"Install this isolated worker: uv sync --project integrations/{framework} --locked"
        )
    # Do not pass provider credentials or the user's bearer token into the worker.
    environment = {
        k: v
        for k, v in os.environ.items()
        if not any(
            word in k.upper() for word in ("TOKEN", "SECRET", "PASSWORD", "KEY", "CREDENTIAL")
        )
    }
    process = await asyncio.create_subprocess_exec(
        str(python),
        str(ROOT / "integrations/worker.py"),
        cwd=ROOT,
        env=environment,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(
                json.dumps(
                    {"framework": framework, "vendor": vendor, "brief": brief, "partner": partner}
                ).encode()
            ),
            timeout=90,
        )
    except BaseException:
        if process.returncode is None:
            process.kill()
            await process.wait()
        raise
    for line in stdout.decode(errors="replace").splitlines():
        if line.startswith("@@MAPLEWOOD_RESULT@@") and process.returncode == 0:
            return json.loads(line.removeprefix("@@MAPLEWOOD_RESULT@@"))
    raise ValueError(f"{framework} worker failed: {stderr.decode(errors='replace')[-1800:]}")
