"""Generate local-only Compose credentials without overwriting an existing setup."""

import json
import secrets
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from common.card_trust import jwks
from common.security import b64
from deploy.keycloak import realm


def main() -> None:
    folder = Path(__file__).resolve().parent / "secrets"
    folder.mkdir(exist_ok=True)
    path = folder / "network.env"
    existing = (
        dict(line.split("=", 1) for line in path.read_text().splitlines() if "=" in line)
        if path.exists()
        else {}
    )
    vendors = ["venues", "catering", "av", "travel", "print", "concierge"]
    tokens = {
        vendor: existing.get(vendor.upper() + "_TOKEN", secrets.token_urlsafe(32))
        for vendor in vendors
    }
    rows = [vendor.upper() + "_TOKEN=" + token for vendor, token in tokens.items()]
    rows += [
        "POSTGRES_PASSWORD=" + existing.get("POSTGRES_PASSWORD", secrets.token_urlsafe(32)),
        "KEYCLOAK_PASSWORD=" + existing.get("KEYCLOAK_PASSWORD", secrets.token_urlsafe(32)),
        "VENDOR_TOKENS="
        + json.dumps(
            {key: value for key, value in tokens.items() if key != "concierge"},
            separators=(",", ":"),
        ),
    ]
    oidc_secret = existing.get("OIDC_CLIENT_SECRET", secrets.token_urlsafe(32))
    rows.append("OIDC_CLIENT_SECRET=" + oidc_secret)
    realm_file = folder / "maplewood-realm.json"
    realm_file.write_text(json.dumps(realm(oidc_secret), indent=2), encoding="utf-8")
    realm_file.chmod(0o600)
    if "TRUSTED_KEYS" in existing:
        rows += [
            name + "=" + value
            for name, value in existing.items()
            if name.endswith("_SIGNING_KEY") or name == "TRUSTED_KEYS"
        ]
    else:
        keys = {vendor: Ed25519PrivateKey.generate() for vendor in vendors}
        rows += [
            vendor.upper() + "_SIGNING_KEY=" + b64(key.private_bytes_raw())
            for vendor, key in keys.items()
        ]
        rows.append(
            "TRUSTED_KEYS="
            + json.dumps(
                {vendor: jwks(key.public_key(), vendor + "-v1") for vendor, key in keys.items()},
                separators=(",", ":"),
            )
        )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    path.chmod(0o600)
    print("Generated ignored deployment credentials.")


if __name__ == "__main__":
    main()
