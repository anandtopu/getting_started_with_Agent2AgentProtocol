"""Verify real framework runtimes and their A2A adapters using synthetic data."""

import argparse
import asyncio
import json

from agents.app import make_handler
from agents.business import quote
from agents.framework_vendor import FrameworkVendor
from common.config import ROOT
from common.frameworks import FRAMEWORKS, framework_quote
from common.protocol import as_dict, request
from common.testing import client


async def check(framework, capture=False):
    brief = {"guests": 40, "date": "2027-06-01", "dietary": {"vegan": 40}}
    result = await framework_quote(framework, "catering", brief)
    assert result == quote("catering", brief), result
    handler = make_handler("catering", executor=FrameworkVendor("catering", framework))
    records = []
    async with client("catering", handler=handler, records=records) as http:
        first = (await http.post("/message:send", json=as_dict(request({"guests": 40})))).json()[
            "task"
        ]
        assert first["status"]["state"] == "TASK_STATE_INPUT_REQUIRED"
        followup = request(
            {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
        )
        result = (await http.post("/message:send", json=as_dict(followup))).json()["task"]
        assert (
            result["id"] == first["id"] and result["status"]["state"] == "TASK_STATE_COMPLETED"
        ), result
        assert result["artifacts"][0]["parts"][0]["data"] == quote("catering", brief)
    if capture:
        path = ROOT / "modules/11_framework_integrations/wire" / (framework + ".jsonl")
        path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
    print(framework + ": isolated runtime and A2A continuation passed.", flush=True)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", choices=FRAMEWORKS)
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    for framework in [args.framework] if args.framework else FRAMEWORKS:
        await check(framework, args.capture)


if __name__ == "__main__":
    asyncio.run(main())
