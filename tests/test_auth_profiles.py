"""Authentication mechanisms, automated rotation and fail-closed JWKS refresh."""

import json
import time

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key

from agents.app import make_app, make_handler
from agents.catalog import card
from common.auth_profiles import secured_card
from common.card_trust import trusted_jwks
from common.identity import RefreshingOIDCVerifier
from common.key_rotation import RotatingCardKeys
from common.protocol import as_dict, request
from common.security import Principal, verify_card


@pytest.mark.parametrize(
    "vendor,scheme",
    [
        ("venues", "http_auth_security_scheme"),
        ("catering", "api_key_security_scheme"),
        ("av", "oauth2_security_scheme"),
        ("travel", "open_id_connect_security_scheme"),
        ("print", "mtls_security_scheme"),
    ],
)
def test_cards_advertise_the_enforced_scheme(vendor, scheme):
    identity = secured_card(card(vendor), vendor)
    assert list(identity.security_schemes.values())[0].HasField(scheme)


async def test_api_key_is_header_only_and_bearer_is_not_a_substitute():
    handler = make_handler("catering")
    app = make_app(
        "catering",
        handler=handler,
        tokens={"fixture": Principal("planner")},
        api_key_header="X-API-Key",
    )
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://test"
        ) as client:
            for headers, status in [
                ({}, 401),
                ({"Authorization": "Bearer fixture"}, 401),
                ({"X-API-Key": "fixture"}, 200),
            ]:
                response = await client.post(
                    "/message:send",
                    headers={"A2A-Version": "1.0", **headers},
                    json=as_dict(request({"guests": 40})),
                )
                assert response.status_code == status
    finally:
        await handler.aclose()


def test_card_rotation_overlap_expiration_and_revocation():
    now = [0]
    service = RotatingCardKeys(card("venues"), interval=100, overlap=30, clock=lambda: now[0])
    first = service.card()
    now[0] = 101
    second = service.card()
    keys = trusted_jwks(service.public_keys())
    verify_card(first, keys)
    verify_card(second, keys)
    now[0] = 132
    with pytest.raises(ValueError):
        verify_card(first, trusted_jwks(service.public_keys()))
    service.revoke(service.current)
    with pytest.raises(ValueError):
        verify_card(second, trusted_jwks(service.public_keys()))


async def test_oidc_rotation_refresh_and_expired_cache_outage():
    private = [generate_private_key(public_exponent=65537, key_size=2048) for _ in range(2)]
    keys = [
        {**json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(k.public_key())), "kid": str(i)}
        for i, k in enumerate(private)
    ]
    clock, generation, reads = [0], [0], []

    def respond(request):
        assert str(request.url) == "https://issuer.test/keys"
        reads.append(1)
        return (
            httpx.Response(200, json={"keys": [keys[generation[0]]]})
            if generation[0] >= 0
            else httpx.Response(503)
        )

    def token(index):
        return jwt.encode(
            {
                "iss": "https://issuer.test",
                "aud": "av",
                "sub": "planner",
                "iat": int(time.time()),
                "exp": int(time.time()) + 60,
                "tenant": "maplewood",
                "scope": "quote",
            },
            private[index],
            algorithm="RS256",
            headers={"kid": str(index)},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        verifier = RefreshingOIDCVerifier(
            client,
            "https://issuer.test/keys",
            "https://issuer.test",
            "av",
            clock=lambda: clock[0],
            ttl=10,
        )
        assert await verifier(token(0))
        assert await verifier(token(1)) is None
        assert len(reads) == 1
        clock[0], generation[0] = 6, 1
        assert await verifier(token(1))
        assert await verifier(token(0)) is None
        clock[0], generation[0] = 17, -1
        assert await verifier(token(1)) is None
