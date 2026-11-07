"""Validate OIDC access tokens against an operator-pinned issuer, audience and JWKS."""

import jwt

from common.security import Principal


class OIDCVerifier:
    def __init__(self, jwks: dict, issuer: str, audience: str):
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
