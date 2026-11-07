"""Authenticated subjects receive independent bounded budgets; expiration frees capacity."""

import httpx
import pytest
from starlette.responses import JSONResponse

from common.limits import RateBudget
from common.security import BearerGate, Principal


async def test_authentication_and_rate_budget():
    now = [1000]
    budget = RateBudget(limit=2, max_identities=2, clock=lambda: now[0])

    async def app(scope, receive, send):
        await JSONResponse({"accepted": True})(scope, receive, send)

    gate = BearerGate(app, {"a": Principal("alice"), "b": Principal("bob")}, rate_budget=budget)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gate), base_url="http://test"
    ) as client:
        assert (await client.post("/rpc")).status_code == 401
        for _ in range(2):
            assert (
                await client.post("/rpc", headers={"Authorization": "Bearer a"})
            ).status_code == 200
        denied = await client.post("/rpc", headers={"Authorization": "Bearer a"})
        assert denied.status_code == 429 and denied.headers["Retry-After"] == "60"
        assert (await client.post("/rpc", headers={"Authorization": "Bearer b"})).status_code == 200
        now[0] += 61
        assert (await client.post("/rpc", headers={"Authorization": "Bearer a"})).status_code == 200


def test_bucket_memory_is_bounded():
    now = [0]
    budget = RateBudget(limit=2, max_identities=2, clock=lambda: now[0])
    assert budget.allow("a") and budget.allow("b")
    assert not budget.allow("c")
    assert len(budget.buckets) == 2
    now[0] = 61
    assert budget.allow("c")
    assert len(budget.buckets) == 1


def test_empty_credentials_are_never_accepted():
    with pytest.raises(ValueError, match="must not be empty"):
        BearerGate(None, {"": Principal("alice")})
