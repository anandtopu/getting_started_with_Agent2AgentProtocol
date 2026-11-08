"""Validate OIDC access tokens against an operator-pinned issuer, audience and JWKS."""

import asyncio
import time

import httpx
import jwt

from common.http_limits import request_json
from common.security import Principal


class OIDCVerifier:
    def __init__(self, jwks: dict, issuer: str, audience: str):
        if not isinstance(jwks, dict):
            raise ValueError("OIDC keys must be a JWKS object.")
        self.keys = jwt.PyJWKSet.from_dict(jwks)
        self.issuer, self.audience = issuer, audience

    def __call__(self, token: str) -> Principal | None:
        try:
            header = jwt.get_unverified_header(token)
            # Algorithms and keys are policy, not a choice made by the token.
            if header.get("alg") != "RS256" or any(
                k in header for k in ("jku", "jwk", "x5u", "crit")
            ):
                return None
            key = self.keys[header["kid"]].key
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            )
            if not isinstance(claims.get("scope", ""), str) or not isinstance(claims["sub"], str):
                return None
            if (
                claims.get("tenant") != "maplewood"
                or "quote" not in claims.get("scope", "").split()
            ):
                return None
            return Principal(
                claims["sub"], "maplewood", "partner" in claims.get("scope", "").split()
            )
        except (jwt.PyJWTError, KeyError, TypeError, ValueError):
            return None


class RefreshingOIDCVerifier:
    """Refresh only an operator-pinned JWKS URL, never token-supplied discovery.

    A bounded cache allows overlapping keys during rotation. Expired cache entries
    fail closed if refresh fails; unknown kids cannot trigger a fetch per request.
    """

    def __init__(
        self, client, jwks_url, issuer, audience, *, ttl=60, cooldown=5, clock=time.monotonic
    ):
        if not jwks_url.startswith("https://") and not jwks_url.startswith("http://keycloak:"):
            raise ValueError("JWKS requires HTTPS (the private Keycloak lab is the only exception)")
        self.client, self.url, self.issuer, self.audience = client, jwks_url, issuer, audience
        self.ttl, self.cooldown, self.clock = ttl, cooldown, clock
        self.verifier, self.updated, self.attempted = None, float("-inf"), float("-inf")
        self.lock = asyncio.Lock()

    async def __call__(self, token):
        try:
            header = jwt.get_unverified_header(token)
            if header.get("alg") != "RS256" or any(
                k in header for k in ("jku", "jwk", "x5u", "crit")
            ):
                return None
        except jwt.PyJWTError:
            return None
        now = self.clock()
        known = self.verifier and any(
            key.key_id == header.get("kid") for key in self.verifier.keys.keys
        )
        if not known or now - self.updated >= self.ttl:
            async with self.lock:
                now = self.clock()
                if now - self.attempted >= self.cooldown:
                    self.attempted = now
                    try:
                        document = await request_json(self.client, "GET", self.url, timeout=3)
                        self.verifier = OIDCVerifier(document, self.issuer, self.audience)
                        self.updated = now
                    except (httpx.HTTPError, ValueError, TypeError, KeyError, jwt.PyJWTError):
                        pass
        if self.verifier is None or self.clock() - self.updated >= self.ttl:
            return None
        return self.verifier(token)
