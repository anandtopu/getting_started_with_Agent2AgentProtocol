"""Local Keycloak-backed venue lab: tokens are obtained outside A2A."""

import argparse
import os
import time

import httpx
import uvicorn
from a2a import types

from agents.app import make_app
from agents.catalog import card
from common.identity import OIDCVerifier


def oidc_card(issuer: str, endpoint: str):
    result = card("venues")
    result.name = "Granite Hall Venues (OIDC lab)"
    result.ClearField("security_schemes")
    result.ClearField("security_requirements")
    result.security_schemes["oidc"].CopyFrom(
        types.SecurityScheme(
            open_id_connect_security_scheme=types.OpenIdConnectSecurityScheme(
                open_id_connect_url=issuer + "/.well-known/openid-configuration"
            )
        )
    )
    result.security_requirements.add(schemes={"oidc": types.StringList(list=["quote"])})
    for interface in result.supported_interfaces:
        interface.url = endpoint + ("/rpc" if interface.protocol_binding == "JSONRPC" else "")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8106)
    args = parser.parse_args()
    # Both URLs are operator configuration. Never use a jku or issuer supplied by a token.
    issuer = os.environ.get("OIDC_ISSUER", "http://127.0.0.1:8080/realms/maplewood")
    jwks_url = os.environ.get("OIDC_JWKS_URL", issuer + "/protocol/openid-connect/certs")
    with httpx.Client(timeout=3, follow_redirects=False) as http:
        for _ in range(120):
            try:
                response = http.get(jwks_url)
                response.raise_for_status()
                verifier = OIDCVerifier(response.json(), issuer, "granite")
                break
            except (httpx.HTTPError, ValueError):
                time.sleep(1)
        else:
            raise SystemExit(
                "Keycloak is unavailable. Start the deployment described in deploy/README.md."
            )
    app = make_app(
        "venues", verifier=verifier, agent_card=oidc_card(issuer, f"http://127.0.0.1:{args.port}")
    )
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
