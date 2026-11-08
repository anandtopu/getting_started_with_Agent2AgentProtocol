"""Reproducible Compose overlays for encrypted and mixed-framework networks."""

import json

from common.config import PORTS, ROOT


def main():
    endpoints = {vendor: f"https://{vendor}:{port}" for vendor, port in PORTS.items()}
    services = {}
    for vendor in PORTS:
        env = {
            "MAPLEWOOD_HARDENED": "1",
            "MAPLEWOOD_VENDOR_URLS": json.dumps(endpoints),
            "MAPLEWOOD_TLS_CERT": f"/course/deploy/secrets/tls/{vendor}.pem",
            "MAPLEWOOD_TLS_KEY": f"/course/deploy/secrets/tls/{vendor}-key.pem",
            "MAPLEWOOD_TLS_CA": "/course/deploy/secrets/tls/ca.pem",
            "OIDC_ISSUER": "https://localhost:8443/realms/maplewood",
            "OIDC_JWKS_URL": "https://keycloak:8443/realms/maplewood/protocol/openid-connect/certs",
            "OIDC_TOKEN_URL": "https://keycloak:8443/realms/maplewood/protocol/openid-connect/token",
        }
        files = ["ca.pem", vendor + ".pem", vendor + "-key.pem"]
        if vendor == "concierge":
            files += ["client.pem", "client-key.pem"]
            env.update(
                {
                    "MAPLEWOOD_CLIENT_CERT": "/course/deploy/secrets/tls/client.pem",
                    "MAPLEWOOD_CLIENT_KEY": "/course/deploy/secrets/tls/client-key.pem",
                    "OIDC_CLIENT_SECRET": "${OIDC_CLIENT_SECRET}",
                }
            )
        services[vendor] = {
            "environment": env,
            "volumes": [
                f"./secrets/tls/{name}:/course/deploy/secrets/tls/{name}:ro" for name in files
            ],
        }
    services["keycloak"] = {
        "environment": {
            "KC_HOSTNAME": "https://localhost:8443",
            "KC_HTTP_ENABLED": "false",
            "KC_HTTPS_CERTIFICATE_FILE": "/opt/keycloak/conf/tls/keycloak.pem",
            "KC_HTTPS_CERTIFICATE_KEY_FILE": "/opt/keycloak/conf/tls/keycloak-key.pem",
        },
        "ports": ["127.0.0.1:8443:8443"],
        "volumes": [
            f"./secrets/tls/{name}:/opt/keycloak/conf/tls/{name}:ro"
            for name in ("keycloak.pem", "keycloak-key.pem")
        ],
    }
    # The separate introductory OIDC lab belongs only to the unencrypted local profile.
    services["oidc-venue"] = {"profiles": ["legacy-oidc-lab"]}
    (ROOT / "deploy/hardened.yml").write_text(
        json.dumps({"services": services}, indent=2) + "\n", encoding="utf-8"
    )
    frameworks = {
        "venues": "adk",
        "catering": "strands",
        "av": "pydantic",
        "travel": "crewai",
        "print": "beeai",
    }
    overlay = {
        name: {
            "build": {"args": {"FRAMEWORK": framework}},
            "command": [
                "uv",
                "run",
                "--no-sync",
                "maplewood",
                "--vendor",
                name,
                "--host",
                "0.0.0.0",
                "--framework",
                framework,
            ],
            "environment": {"MAPLEWOOD_VENDOR_TIMEOUT": "90"},
        }
        for name, framework in frameworks.items()
    }
    overlay["concierge"] = {"environment": {"MAPLEWOOD_VENDOR_TIMEOUT": "90"}}
    (ROOT / "deploy/frameworks.yml").write_text(
        json.dumps({"services": overlay}, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
