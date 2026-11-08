"""Scripted selection crosses real vendor boundaries while personal data stays local."""

import pytest

from agents.concierge import Concierge
from common.fakes import ScriptedModel
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
