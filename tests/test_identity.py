"""Wrong issuer, audience, scope, expiration and signatures cannot authorize a quote."""

import json
import time

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key

from agents.app import make_app, make_handler
from common.identity import OIDCVerifier
from common.protocol import as_dict, request


@pytest.mark.parametrize(
    "mutation",
    ["valid", "issuer", "audience", "expired", "scope", "scope_type", "tenant", "signature", "jku"],
)
async def test_oidc_boundary(mutation):
    private = generate_private_key(public_exponent=65537, key_size=2048)
    key = {**json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key())), "kid": "trusted"}
    verifier = OIDCVerifier({"keys": [key]}, "https://issuer.test", "granite")
    claims = {
        "iss": "https://issuer.test",
        "aud": "granite",
        "sub": "concierge",
        "iat": int(time.time()),
        "exp": int(time.time()) + 60,
        "tenant": "maplewood",
        "scope": "quote",
    }
    changes = {
        "issuer": ("iss", "https://rogue.test"),
        "audience": ("aud", "other"),
        "expired": ("exp", 1),
        "scope": ("scope", "read"),
        "scope_type": ("scope", ["quote"]),
        "tenant": ("tenant", "other"),
    }
    if mutation in changes:
        field, value = changes[mutation]
        claims[field] = value
    if mutation == "signature":
        private = generate_private_key(public_exponent=65537, key_size=2048)
    headers = {"kid": "trusted"}
    if mutation == "jku":
        headers["jku"] = "https://rogue.test/keys"
    token = jwt.encode(claims, private, algorithm="RS256", headers=headers)
    handler = make_handler("venues")
    app = make_app("venues", verifier=verifier, handler=handler)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"A2A-Version": "1.0"},
    ) as http:
        response = await http.post(
            "/message:send",
            headers={"Authorization": "Bearer " + token},
            json=as_dict(request({"guests": 40})),
        )
        assert response.status_code == (200 if mutation == "valid" else 401)
    await handler.aclose()
