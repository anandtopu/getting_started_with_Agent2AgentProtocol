"""Keys come from operator configuration, never a URL nominated by an untrusted card."""

import json
import os

from a2a.types import AgentCard
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from google.protobuf.json_format import ParseDict

from common.http_limits import request_json
from common.protocol import as_dict
from common.security import b64, sign_card, unb64, verify_card


def published_card(card: AgentCard, vendor: str) -> AgentCard:
    key = os.environ.get("MAPLEWOOD_SIGNING_KEY")
    if not key:
        return card
    private = Ed25519PrivateKey.from_private_bytes(unb64(key))
    return ParseDict(sign_card(as_dict(card), private, vendor + "-v1"), AgentCard())


def jwks(public_key: Ed25519PublicKey, kid: str) -> dict:
    return {
        "keys": [
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "use": "sig",
                "alg": "EdDSA",
                "kid": kid,
                "x": b64(public_key.public_bytes_raw()),
            }
        ]
    }


def trusted_jwks(document: dict) -> dict[str, Ed25519PublicKey]:
    if not isinstance(document, dict) or not isinstance(document.get("keys"), list):
        raise ValueError("Card signing keys must be a JWKS object.")
    result = {}
    for key in document["keys"]:
        if not isinstance(key, dict) or not all(isinstance(key.get(k), str) for k in ("kid", "x")):
            raise ValueError("Malformed card signing key")
        if key.get("kty") != "OKP" or key.get("crv") != "Ed25519" or key.get("use") != "sig":
            raise ValueError("Unsupported card signing key")
        if key["kid"] in result:
            raise ValueError("Duplicate key ID")
        result[key["kid"]] = Ed25519PublicKey.from_public_bytes(unb64(key["x"]))
    return result


def verify_vendor(card: dict, vendor: str) -> dict:
    trust = json.loads(os.environ.get("MAPLEWOOD_TRUSTED_KEYS", "{}"))
    if vendor not in trust:
        raise ValueError("No out-of-band card key configured for vendor")
    return verify_card(card, trusted_jwks(trust[vendor]))


async def verify_discovered(card: dict, vendor: str, client):
    if os.environ.get("MAPLEWOOD_HARDENED") != "1":
        return verify_vendor(card, vendor)
    from common.config import url

    endpoint = url(vendor)
    if not endpoint.startswith("https://"):
        raise ValueError("Rotating card trust requires a configured HTTPS vendor endpoint")
    document = await request_json(client, "GET", endpoint + "/.well-known/jwks.json", timeout=3)
    return verify_card(card, trusted_jwks(document))
