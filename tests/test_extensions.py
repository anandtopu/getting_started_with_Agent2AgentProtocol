"""The optional extension is explicit in the request and resulting artifact."""

from agents.catalog import QUOTE_EXTENSION
from common.protocol import as_dict, request
from common.testing import client


async def test_extension_is_opt_in():
    async with client("venues") as http:
        plain = (await http.post("/message:send", json=as_dict(request({"guests": 40})))).json()[
            "task"
        ]
        extended = (
            await http.post(
                "/message:send",
                headers={"A2A-Extensions": QUOTE_EXTENSION},
                json=as_dict(request({"guests": 40})),
            )
        ).json()["task"]
        assert not plain["artifacts"][0].get("extensions")
        assert extended["artifacts"][0]["extensions"] == [QUOTE_EXTENSION]
