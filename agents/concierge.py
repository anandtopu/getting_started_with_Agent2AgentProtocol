"""A bounded orchestrator. Remote artifacts are data, never executable instructions."""

import asyncio
import json

import httpx
from jsonschema import ValidationError, validate

from common.protocol import request
from common.remote import send

QUOTE_SCHEMA = {
    "type": "object",
    "required": ["vendor", "total_cents", "currency", "approved"],
    "properties": {
        "vendor": {"type": "string"},
        "selection": {"type": "string"},
        "guests": {"type": "integer", "minimum": 1, "maximum": 1000},
        "total_cents": {"type": "integer", "minimum": 0},
        "currency": {"const": "USD"},
        "approved": {"const": False},
    },
    "additionalProperties": False,
}


class Concierge:
    def __init__(
        self, clients: dict[str, httpx.AsyncClient], model=None, fallbacks=None, skills=None
    ):
        self.clients = clients
        self.model = model
        self.fallbacks = fallbacks or {}
        self.skills = skills or {name: [name + ".quote"] for name in clients}

    async def plan(self, brief: dict, previous: dict | None = None) -> dict:
        vendors = brief.get("needs", ["venues", "catering"])
        if previous:
            vendors = [item["vendor"] for item in previous["delegations"]]
        elif self.model:
            model_brief = {
                key: brief[key]
                for key in ("guests", "date", "dietary", "rooms", "needs")
                if key in brief
            }
            prompt = (
                "Select vendors for the event's requested needs. Call select_action with "
                'arguments {"vendors":[vendor names]}. Use vendor names, not skill IDs. '
                "Verified vendor-to-skills mapping (JSON): "
                + json.dumps(self.skills, sort_keys=True)
                + ". Event data (JSON): "
                + json.dumps(model_brief, sort_keys=True)
            )
            schema = {
                "type": "object",
                "properties": {
                    "vendors": {
                        "type": "array",
                        "items": {"type": "string", "enum": list(self.clients)},
                        "minItems": 1,
                        "maxItems": 5,
                        "uniqueItems": True,
                    }
                },
                "required": ["vendors"],
                "additionalProperties": False,
            }
            decision = (
                await self.model.tool_decide(prompt, schema)
                if hasattr(self.model, "tool_decide")
                else await self.model.decide(prompt)
            )
            vendors = decision.get("vendors", [])
        if (
            not isinstance(vendors, list)
            or not all(isinstance(v, str) for v in vendors)
            or not vendors
            or len(vendors) > 5
            or len(set(vendors)) != len(vendors)
            or any(v not in self.clients for v in vendors)
        ):
            raise ValueError("Delegation must name up to five distinct trusted vendors.")

        async def delegate(vendor: str):
            prior = next(
                (d for d in (previous or {}).get("delegations", []) if d["vendor"] == vendor), None
            )
            if prior and prior["state"] == "TASK_STATE_COMPLETED":
                return prior
            # Each client was provisioned with its own vendor token, never a user's token.
            payload = {
                key: brief[key] for key in ("guests", "date", "dietary", "rooms") if key in brief
            }
            try:
                continuation = prior and prior["state"] in {
                    "TASK_STATE_INPUT_REQUIRED",
                    "TASK_STATE_AUTH_REQUIRED",
                }
                message = request(
                    payload,
                    task_id=prior["task_id"] if continuation else "",
                    context_id=prior["context_id"] if continuation else "",
                )
                try:
                    task = (await send(self.clients[vendor], message))["task"]
                except httpx.TransportError:
                    # A paused task belongs to its original server. Never send its ID
                    # to a fallback. A new read-only quote may use an operator-approved backup.
                    if continuation or vendor not in self.fallbacks:
                        raise
                    task = (await send(self.fallbacks[vendor], request(payload)))["task"]
                artifacts = task.get("artifacts", [])
                quotes = [
                    part["data"]
                    for artifact in artifacts
                    for part in artifact["parts"]
                    if "data" in part
                ]
                for quote in quotes:
                    validate(quote, QUOTE_SCHEMA)
                    if quote["vendor"] != vendor:
                        raise ValueError("Vendor identity in quote does not match delegate.")
                return {
                    "vendor": vendor,
                    "task_id": task["id"],
                    "context_id": task["contextId"],
                    "state": task["status"]["state"],
                    "quotes": quotes,
                    "question": task["status"].get("message"),
                }
            except (httpx.HTTPError, KeyError, ValueError, ValidationError) as exc:
                return {
                    "vendor": vendor,
                    "state": "TASK_STATE_FAILED",
                    "error": str(exc),
                    "quotes": [],
                }

        delegations = await asyncio.gather(*(delegate(vendor) for vendor in vendors))
        total = sum(q["total_cents"] for item in delegations for q in item["quotes"])
        result = {
            "delegations": delegations,
            "total_cents": total,
            "within_budget": total <= brief.get("budget_cents", 0),
            "approval_required": True,
        }
        if brief.get("tentative_holds"):
            if not {"venues", "travel"} <= set(vendors):
                raise ValueError("Tentative holds require venue and travel delegates")
            if all(d["state"] == "TASK_STATE_COMPLETED" for d in delegations):
                from common.saga import reserve_pair

                hold_request = brief.get("hold_request_id")
                if not isinstance(hold_request, str) or not 1 <= len(hold_request) <= 100:
                    raise ValueError("Provide a stable hold_request_id for safe retries")
                result["reservations"] = await reserve_pair(
                    self.clients["travel"], self.clients["venues"], hold_request
                )
        return result
