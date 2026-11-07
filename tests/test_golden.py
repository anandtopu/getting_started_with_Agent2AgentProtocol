"""Golden scenarios are committed expectations, not regenerated during evaluation."""

import json
from contextlib import AsyncExitStack

import pytest

from agents.concierge import Concierge
from common.config import ROOT
from common.data import load
from common.lessons import events
from common.protocol import as_dict, request
from common.testing import client

SCENARIOS = [
    json.loads(line) for line in (ROOT / "data/eval/golden.jsonl").read_text().splitlines()
]


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s["brief"])
async def test_end_to_end_scenario(scenario):
    brief = load("events/" + scenario["brief"] + ".json")
    async with AsyncExitStack() as stack:
        clients = {
            vendor: await stack.enter_async_context(client(vendor))
            for vendor in scenario["delegations"]
        }
        plan = await Concierge(clients).plan(brief)
        assert [d["vendor"] for d in plan["delegations"]] == scenario["delegations"]
        assert plan["approval_required"]
        assert plan["total_cents"] == sum(
            q["total_cents"] for d in plan["delegations"] for q in d["quotes"]
        )
        response = await clients["catering"].post("/message:stream", json=as_dict(request(brief)))
        observed = events(response.text)
        states = [
            event["task"]["status"]["state"]
            if "task" in event
            else event["statusUpdate"]["status"]["state"]
            for event in observed
            if "task" in event or "statusUpdate" in event
        ]
        assert states == scenario["catering_states"]
        artifacts = [
            event["artifactUpdate"]["artifact"]["artifactId"]
            for event in observed
            if "artifactUpdate" in event
        ]
        assert artifacts == scenario["artifacts"]
        catering = next(d for d in plan["delegations"] if d["vendor"] == "catering")
        assert catering["state"] == states[-1]
