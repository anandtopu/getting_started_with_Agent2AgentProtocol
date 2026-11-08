"""Hardened network: API key, OAuth client credentials, OIDC and mutual TLS."""

import os

import httpx
from a2a import types

from common.identity import RefreshingOIDCVerifier
from common.tls import client_context


def secured_card(identity, vendor):
    identity.ClearField("security_schemes")
    identity.ClearField("security_requirements")
    issuer = os.environ.get("OIDC_ISSUER", "https://localhost:8443/realms/maplewood")
    if vendor == "catering":
        name, scheme = (
            "api_key",
            types.SecurityScheme(
                api_key_security_scheme=types.APIKeySecurityScheme(
                    location="header", name="X-API-Key"
                )
            ),
        )
    elif vendor == "av":
        name, scheme = (
            "oauth",
            types.SecurityScheme(
                oauth2_security_scheme=types.OAuth2SecurityScheme(
                    flows=types.OAuthFlows(
                        client_credentials=types.ClientCredentialsOAuthFlow(
                            token_url=issuer + "/protocol/openid-connect/token",
                            scopes={"quote": "Request quotes"},
                        )
                    )
                )
            ),
        )
    elif vendor == "travel":
        name, scheme = (
            "oidc",
            types.SecurityScheme(
                open_id_connect_security_scheme=types.OpenIdConnectSecurityScheme(
                    open_id_connect_url=issuer + "/.well-known/openid-configuration"
                )
            ),
        )
    elif vendor == "print":
        name, scheme = (
            "mtls",
            types.SecurityScheme(
                mtls_security_scheme=types.MutualTlsSecurityScheme(
                    description="A CA-issued maplewood-concierge client certificate is required."
                )
            ),
        )
    else:
        name, scheme = (
            "bearer",
            types.SecurityScheme(
                http_auth_security_scheme=types.HTTPAuthSecurityScheme(scheme="Bearer")
            ),
        )
    identity.security_schemes[name].CopyFrom(scheme)
    identity.security_requirements.add(
        schemes={name: types.StringList(list=["quote"] if vendor in {"av", "travel"} else [])}
    )
    return identity


def server_auth(vendor):
    if vendor == "catering":
        return {"api_key_header": "X-API-Key"}
    if vendor not in {"av", "travel"}:
        return {}
    client = httpx.AsyncClient(verify=client_context())
    verifier = RefreshingOIDCVerifier(
        client, os.environ["OIDC_JWKS_URL"], os.environ["OIDC_ISSUER"], vendor
    )
    return {"verifier": verifier, "auth_client": client}


async def vendor_headers(vendor, token):
    headers = {"A2A-Version": "1.0"}
    if os.environ.get("MAPLEWOOD_HARDENED") != "1":
        return {**headers, "Authorization": "Bearer " + token}
    if vendor == "catering":
        return {**headers, "X-API-Key": token}
    if vendor in {"av", "travel"}:
        async with httpx.AsyncClient(verify=client_context(), timeout=5) as http:
            response = await http.post(
                os.environ["OIDC_TOKEN_URL"],
                data={
                    "grant_type": "client_credentials",
                    "client_id": "concierge-" + vendor,
                    "client_secret": token,
                    "scope": "quote",
                },
            )
            response.raise_for_status()
            token = response.json()["access_token"]
    return {**headers, "Authorization": "Bearer " + token}
