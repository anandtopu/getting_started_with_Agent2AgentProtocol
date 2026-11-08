"""Acceptance contracts for complete HTTP, task, stream and trust exercises."""

import base64
import xml.etree.ElementTree as ET

import httpx

from agents.app import make_app, make_handler
from common.protocol import as_dict, request
from common.security import Principal
from common.testing import client


async def check(kind, learner):
    family, action = kind.split(":")
    vendor = "catering" if family == "lifecycle" else "av" if family == "stream" else "venues"
    if family == "parts" and action == "multi_part":
        vendor = "catering"
    for guests in (40, 60):
        records = []
        async with client(vendor, records=records) as http:
            brief = {"guests": guests, "dietary": {"vegan": guests}}
            if family == "lifecycle":
                first = (
                    await http.post("/message:send", json=as_dict(request({"guests": guests})))
                ).json()["task"]
                result = await learner.exercise(http, brief, first)
                if action == "resume":
                    assert result["id"] == first["id"] and result["contextId"] == first["contextId"]
                    assert result["status"]["state"] == "TASK_STATE_COMPLETED"
                    assert result["artifacts"][0]["parts"][0]["data"]["guests"] == guests
                elif action == "cancel":
                    assert (
                        result["id"] == first["id"]
                        and result["status"]["state"] == "TASK_STATE_CANCELED"
                    )
                    after = await http.get("/tasks/" + first["id"])
                    assert after.json()["status"]["state"] == "TASK_STATE_CANCELED"
                elif action == "history":
                    assert result["id"] == first["id"] and len(result.get("history", [])) == 1
                elif action == "list":
                    assert len(result["tasks"]) == 1 and result["nextPageToken"]
                elif action == "auth":
                    assert result["status"]["state"] == "TASK_STATE_AUTH_REQUIRED"
                elif action == "rejected":
                    assert result["status"]["state"] == "TASK_STATE_REJECTED"
            elif family == "client":
                result = await learner.exercise(http, brief, None)
                if action in {"rpc", "rest", "sdk"}:
                    assert result["status"]["state"] == "TASK_STATE_COMPLETED"
                    assert result["artifacts"][0]["parts"][0]["data"]["guests"] == guests
                elif action == "poll":
                    assert (
                        result["created"] == result["polled"]
                        and result["state"] == "TASK_STATE_COMPLETED"
                    )
                elif action == "missing":
                    assert result["status"] == 404 and result["reason"] == "TASK_NOT_FOUND"
                elif action == "correlation":
                    assert result["rpc_id"] == "client-" + str(guests)
                    assert result["task_id"] != result["rpc_id"] and result["context_id"]
            elif family == "stream":
                result = await learner.exercise(http, brief, None)
                if action == "status":
                    assert result == [
                        "TASK_STATE_SUBMITTED",
                        "TASK_STATE_WORKING",
                        "TASK_STATE_COMPLETED",
                    ]
                elif action == "chunks":
                    assert result == "Microphone check. Projector alignment. Sound check complete."
                elif action == "flags":
                    assert result == [[False, False], [True, False], [True, True]]
                elif action == "identity":
                    assert result["same_task"] and result["same_context"] and result["events"] >= 7
                elif action == "quote":
                    assert result["vendor"] == "av" and result["guests"] == guests
                elif action == "snapshot":
                    assert result["state"] == "TASK_STATE_COMPLETED" and result["artifact_ids"] == [
                        "plan",
                        "quote",
                    ]
            elif family == "discovery":
                result = await learner.exercise(http, brief, None)
                if action == "interfaces":
                    assert result == ["JSONRPC", "HTTP+JSON"]
                elif action == "skill":
                    assert result["id"] == "venues.quote" and "events" in result["tags"]
                elif action == "capabilities":
                    assert result == {"streaming": True, "push": False, "extended": False}
                elif action == "media":
                    assert set(result) == {
                        "text/plain",
                        "application/json",
                        "application/octet-stream",
                    }
                elif action == "security":
                    assert result == {"scheme": "Bearer", "required": ["vendor_token"]}
                elif action == "validate":
                    assert result["name"] == "Granite Hall Venues" and result["version"] == "1.0.0"
            elif family == "parts":
                result = await learner.exercise(http, brief, None)
                if action == "floor_plan":
                    assert ET.fromstring(base64.b64decode(result["raw"])).tag.endswith("svg")
                    assert result["mediaType"] == "image/svg+xml"
                elif action == "data":
                    assert result["vendor"] == "venues" and result["guests"] == guests
                elif action == "raw_input":
                    assert result["status"]["state"] == "TASK_STATE_COMPLETED"
                elif action == "artifact_ids":
                    assert result == ["floor-plan", "quote"]
                elif action == "unsupported":
                    assert result == 400
                elif action == "multi_part":
                    assert result["data"]["guests"] == guests
                    assert base64.b64decode(result["file"]["raw"]).startswith(b"%PDF-")
            elif family == "conformance":
                result = await learner.exercise(http, brief, None)
                expected = {
                    "parse": -32700,
                    "method": -32601,
                    "missing": -32001,
                    "media": -32005,
                    "version": -32009,
                    "rest_media": "application/a2a+json",
                }
                assert result == expected[action], (
                    "Return the protocol-level rejection, not a fabricated local error."
                )
        assert records, "Exercise must contact the in-process agent."
    if family == "security":
        raise AssertionError("Security uses the dedicated adversarial fixture")


async def security_check(action, learner):
    handler = make_handler("travel")
    tokens = {
        "owner": Principal("one"),
        "stranger": Principal("two"),
        "partner": Principal("one", partner=True),
    }
    app = make_app("travel", handler=handler, tokens=tokens)
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
            headers={"A2A-Version": "1.0"},
        ) as http:
            created = (
                await http.post(
                    "/message:send",
                    headers={"Authorization": "Bearer owner"},
                    json=as_dict(request({"guests": 40})),
                )
            ).json()["task"]
            result = await learner.exercise(http, {"guests": 40}, created)
            expected = {
                "anonymous": 401,
                "owner": 404,
                "tenant": 403,
                "extended_denied": 403,
                "extended_partner": "travel.partner_quote",
                "body_secret": 401,
            }
            assert result == expected[action]
    finally:
        await handler.aclose()


async def push_check(action, learner):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    from common.vendor_kit import vendor_kit
    from common.webhooks import receiver

    endpoint, secret = "https://receiver.test/notifications", b"offline-callback-key"
    sink = receiver(secret)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=sink)) as callback:
        async with vendor_kit(
            "sqlite+aiosqlite:///:memory:",
            {"owner": Principal("planner")},
            Ed25519PrivateKey.generate(),
            callback,
            {endpoint: secret},
        ) as (app, handler):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="https://vendor.test",
                headers={"Authorization": "Bearer owner", "A2A-Version": "1.0"},
            ) as http:
                first = (
                    await http.post("/message:send", json=as_dict(request({"guests": 40})))
                ).json()["task"]
                first["url"] = endpoint
                path = "/tasks/" + first["id"] + "/pushNotificationConfigs"
                if action not in {"create", "ssrf"}:
                    await http.post(
                        path, json={"taskId": first["id"], "id": "planner", "url": endpoint}
                    )
                result = await learner.exercise(http, {"dietary": {"vegan": 40}}, first)
                if action in {"create", "get"}:
                    assert (
                        result["id"] == "planner"
                        and result["url"] == endpoint
                        and result["taskId"] == first["id"]
                    )
                elif action == "list":
                    assert result["configs"][0]["id"] == "planner"
                elif action == "delete":
                    assert result == 200
                    assert not (await http.get(path)).json().get("configs", [])
                elif action == "ssrf":
                    assert result == 400
                elif action == "delivery":
                    await handler.aclose()
                    assert result["status"]["state"] == "TASK_STATE_COMPLETED"
                    assert sink.state.deliveries and any(
                        d.get("statusUpdate", {}).get("status", {}).get("state")
                        == "TASK_STATE_COMPLETED"
                        for d in sink.state.deliveries
                    )
