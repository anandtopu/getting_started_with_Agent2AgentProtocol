"""Negative tests make security properties observable."""

import httpx
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from agents.app import make_app
from agents.catalog import card
from common.protocol import as_dict, request
from common.security import (
    Principal,
    safe_file_url,
    sign_card,
    verify_card,
    verify_webhook,
    webhook_headers,
)


async def test_auth_and_ownership():
    app = make_app(tokens={"alice-token": Principal("alice"), "bob-token": Principal("bob")})
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"A2A-Version": "1.0"},
    ) as http:
        assert (await http.get("/.well-known/agent-card.json")).status_code == 200
        assert (await http.post("/message:send", json=as_dict(request({})))).status_code == 401
        created = await http.post(
            "/message:send",
            headers={"Authorization": "Bearer alice-token"},
            json=as_dict(request({})),
        )
        task = created.json()["task"]
        denied = await http.get(
            f"/tasks/{task['id']}", headers={"Authorization": "Bearer bob-token"}
        )
        assert denied.status_code == 404


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/secret",
        "https://10.0.0.1/secret",
        "https://[::1]/secret",
        "https://169.254.169.254/latest",
        "file:///etc/passwd",
        "https://example.com/secret",
    ],
)
def test_file_ssrf(url):
    with pytest.raises(ValueError):
        safe_file_url(url, {url})


def test_signing_and_forgery():
    key = Ed25519PrivateKey.generate()
    signed = sign_card(as_dict(card("venues")), key, "vendor-1")
    assert verify_card(signed, {"vendor-1": key.public_key()})["name"] == "Granite Hall Venues"
    signed["name"] = "Attacker"
    with pytest.raises(ValueError):
        verify_card(signed, {"vendor-1": key.public_key()})


def test_replay_and_tamper():
    secret, body, seen = b"unit-test-secret", b'{"task":{}}', {}
    headers = webhook_headers(body, secret, "delivery-1", now=1000)
    with pytest.raises(ValueError):
        verify_webhook(body + b" ", headers, secret, seen, now=1000)
    verify_webhook(body, headers, secret, seen, now=1000)
    with pytest.raises(ValueError):
        verify_webhook(body, headers, secret, seen, now=1000)
