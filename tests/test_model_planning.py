"""Scripted selection crosses real vendor boundaries while personal data stays local."""

import copy
import json

import httpx
import pytest
from jsonschema import ValidationError

from agents.concierge import Concierge
from common.config import Settings
from common.fakes import ScriptedModel
from common.llm import Model
from common.model_streams import openai_wire_schema
from common.testing import client


async def test_model_sees_skills_but_not_private_fields():
    model = ScriptedModel([{"vendors": ["venues"]}])
    async with client("venues") as venue:
        result = await Concierge({"venues": venue}, model=model).plan(
            {"guests": 40, "private_note": "secret diary", "user_token": "secret bearer"}
        )
    assert result["delegations"][0]["state"] == "TASK_STATE_COMPLETED"
    assert "Provide a venues quote." in model.calls[0]
    assert "secret" not in model.calls[0]
    assert result["approval_required"]


@pytest.mark.parametrize(
    "selection",
    [
        [],
        "venues",
        [None],
        [{"url": "https://rogue.test"}],
        ["venues", "venues"],
        ["rogue"],
        ["venues.quote"],
    ],
)
async def test_model_cannot_expand_trust(selection):
    model = ScriptedModel([{"vendors": selection}])
    with pytest.raises(ValueError, match="trusted vendors"):
        await Concierge({"venues": None}, model=model).plan({"guests": 40})


@pytest.mark.parametrize("vendors", [["venues"], ["venues", "venues"], [], ["rogue"]])
async def test_openai_concierge_schema_keeps_local_constraints(vendors, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "offline-fixture-key")
    requests = []

    def respond(request):
        body = json.loads(request.content)
        requests.append(body)
        function = body["tools"][0]
        assert function["strict"] is True
        schema = function["parameters"]["properties"]["vendors"]
        assert "uniqueItems" not in schema
        assert schema["minItems"] == 1 and schema["maxItems"] == 5
        assert schema["items"]["enum"] == ["venues"]
        packets = [
            {
                "type": "response.output_item.added",
                "item": {
                    "id": "call1",
                    "type": "function_call",
                    "name": "select_action",
                    "arguments": "",
                },
            },
            {
                "type": "response.function_call_arguments.delta",
                "item_id": "call1",
                "delta": json.dumps({"vendors": vendors}),
            },
            {"type": "response.completed", "response": {"status": "completed"}},
        ]
        return httpx.Response(200, text="".join("data: " + json.dumps(p) + "\n\n" for p in packets))

    model = Model(
        Settings(llm_provider="openai", llm_model="fixture"), httpx.MockTransport(respond)
    )
    records = []
    async with client("venues", records=records) as venue:
        concierge = Concierge({"venues": venue}, model=model)
        if vendors == ["venues"]:
            plan = await concierge.plan({"guests": 40, "needs": ["venues"]})
            assert plan["delegations"][0]["state"] == "TASK_STATE_COMPLETED"
        else:
            with pytest.raises(ValidationError):
                await concierge.plan({"guests": 40, "needs": ["venues"]})
    assert len(requests) == 1
    if vendors != ["venues"]:
        assert records == [], "Invalid model choices reached the vendor"


def test_openai_schema_projection_preserves_names_literals_and_original():
    schema = {
        "type": "object",
        "properties": {
            "uniqueItems": {"type": "boolean"},
            "groups": {
                "type": "array",
                "uniqueItems": True,
                "items": {
                    "anyOf": [{"type": "array", "uniqueItems": True, "items": {"type": "string"}}]
                },
            },
        },
        "$defs": {"group": {"type": "array", "uniqueItems": True}},
        "default": {"uniqueItems": True},
        "enum": [{"uniqueItems": True}],
    }
    original = copy.deepcopy(schema)
    wire = openai_wire_schema(schema)
    assert schema == original
    assert wire["properties"]["uniqueItems"] == {"type": "boolean"}
    assert wire["default"] == schema["default"] and wire["enum"] == schema["enum"]
    assert "uniqueItems" not in wire["properties"]["groups"]
    assert "uniqueItems" not in wire["properties"]["groups"]["items"]["anyOf"][0]
    assert "uniqueItems" not in wire["$defs"]["group"]
