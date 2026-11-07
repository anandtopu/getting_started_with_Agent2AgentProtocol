"""Generate a local service-account realm; never commit its generated client secret."""


def realm(secret: str) -> dict:
    return {
        "realm": "maplewood",
        "enabled": True,
        "sslRequired": "none",
        "accessTokenLifespan": 120,
        "clientScopes": [
            {
                "name": "quote",
                "protocol": "openid-connect",
                "attributes": {"include.in.token.scope": "true"},
                "protocolMappers": [
                    {
                        "name": "granite-audience",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-audience-mapper",
                        "config": {
                            "included.custom.audience": "granite",
                            "access.token.claim": "true",
                        },
                    }
                ],
            }
        ],
        "clients": [
            {
                "clientId": "concierge",
                "enabled": True,
                "protocol": "openid-connect",
                "publicClient": False,
                "secret": secret,
                "serviceAccountsEnabled": True,
                "standardFlowEnabled": False,
                "directAccessGrantsEnabled": False,
                "defaultClientScopes": ["quote"],
                "protocolMappers": [
                    {
                        "name": "maplewood-tenant",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-hardcoded-claim-mapper",
                        "config": {
                            "claim.name": "tenant",
                            "claim.value": "maplewood",
                            "jsonType.label": "String",
                            "access.token.claim": "true",
                        },
                    }
                ],
            }
        ],
    }
