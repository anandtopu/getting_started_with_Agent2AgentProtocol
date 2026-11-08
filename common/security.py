"""Small security boundaries with explicit policy and no implicit remote trust."""

import base64
import hashlib
import hmac
import inspect
import ipaddress
import json
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx
import jcs
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from starlette.authentication import SimpleUser
from starlette.responses import JSONResponse

from common.limits import RateBudget


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant: str = "maplewood"
    partner: bool = False


class BearerGate:
    """Authenticate before routing; an untrusted tenant header never grants access."""

    def __init__(
        self,
        app,
        tokens: dict[str, Principal],
        max_bytes: int = 1_000_000,
        verifier=None,
        rate_budget=None,
        api_key_header=None,
    ):
        self.app, self.tokens, self.max_bytes = app, tokens, max_bytes
        if any(not secret for secret in tokens):
            raise ValueError("Authentication tokens must not be empty.")
        self.verifier = verifier
        self.api_key_header = api_key_header
        self.rate_budget = rate_budget or RateBudget()

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or scope["path"] in (
            "/.well-known/agent-card.json",
            "/.well-known/jwks.json",
            "/health",
        ):
            await self.app(scope, receive, send)
            return
        headers = {k.decode().lower(): v.decode() for k, v in scope["headers"]}
        scheme, _, token = headers.get("authorization", "").partition(" ")
        if scheme.lower() != "bearer":
            token = ""
        if self.api_key_header:
            token = headers.get(self.api_key_header.lower(), "")
        principal = next(
            (p for secret, p in self.tokens.items() if hmac.compare_digest(secret, token)), None
        )
        if self.verifier:
            principal = self.verifier(token)
            if inspect.isawaitable(principal):
                principal = await principal
        if not principal:
            await JSONResponse(
                {"error": "Authentication required"}, 401, headers={"WWW-Authenticate": "Bearer"}
            )(scope, receive, send)
            return
        if headers.get("x-tenant", principal.tenant) != principal.tenant:
            await JSONResponse({"error": "Tenant not authorized"}, 403)(scope, receive, send)
            return
        allowed = self.rate_budget.allow(f"{principal.tenant}:{principal.subject}")
        if inspect.isawaitable(allowed):
            allowed = await allowed
        if not allowed:
            await JSONResponse(
                {"error": "Request budget exceeded"}, 429, headers={"Retry-After": "60"}
            )(scope, receive, send)
            return
        body = bytearray()
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            body.extend(event.get("body", b""))
            if len(body) > self.max_bytes:
                await JSONResponse({"error": "Request too large"}, 413)(scope, receive, send)
                return
            if not event.get("more_body"):
                break
        try:
            payload = json.loads(body) if body else {}
        except ValueError:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        params = payload.get("params", payload)
        tenant = params.get("tenant", "") if isinstance(params, dict) else ""
        if tenant and tenant != principal.tenant:
            await JSONResponse({"error": "Tenant not authorized"}, 403)(scope, receive, send)
            return
        extended = (
            scope["path"].endswith("/extendedAgentCard")
            or payload.get("method") == "GetExtendedAgentCard"
        )
        if extended and not principal.partner:
            await JSONResponse({"error": "Partner scope required"}, 403)(scope, receive, send)
            return
        scope["user"] = SimpleUser(f"{principal.tenant}:{principal.subject}")
        scope.setdefault("state", {})["principal"] = principal
        delivered = False

        async def replay_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay_receive, send)


def safe_file_url(url: str, allowed: set[str]) -> str:
    """Use explicit public IP origins; names are rejected to avoid DNS rebinding."""
    parsed = urlsplit(url)
    if (
        url not in allowed
        or parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise ValueError("File URL is not explicitly trusted.")
    try:
        address = ipaddress.ip_address(parsed.hostname or "")
    except ValueError as exc:
        raise ValueError(
            "Use an approved public IP URL or inline bytes; DNS names require a pinned egress proxy."
        ) from exc
    if not address.is_global or parsed.port not in (None, 443):
        raise ValueError("Private, reserved and non-HTTPS destinations are blocked.")
    return url


async def fetch_file(
    url: str, allowed: set[str], client: httpx.AsyncClient, limit: int = 1_000_000
) -> bytes:
    safe_file_url(url, allowed)
    content = bytearray()
    async with client.stream("GET", url, follow_redirects=False, timeout=5) as response:
        if response.status_code != 200:
            raise ValueError("File fetch must return 200 without redirects.")
        async for chunk in response.aiter_bytes():
            content.extend(chunk)
            if len(content) > limit:
                raise ValueError("File exceeds size limit.")
    return bytes(content)


def b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def sign_card(card: dict, private: Ed25519PrivateKey, kid: str) -> dict:
    unsigned = {key: value for key, value in card.items() if key != "signatures"}
    protected = b64(jcs.canonicalize({"alg": "EdDSA", "kid": kid}))
    signing_input = (protected + "." + b64(jcs.canonicalize(unsigned))).encode()
    return {
        **unsigned,
        "signatures": [{"protected": protected, "signature": b64(private.sign(signing_input))}],
    }


def verify_card(card: dict, trusted_keys: dict[str, Ed25519PublicKey]) -> dict:
    if not isinstance(card, dict) or not isinstance(card.get("signatures"), list):
        raise ValueError("A card must contain a signature list.")
    unsigned = {key: value for key, value in card.items() if key != "signatures"}
    for signature in card.get("signatures", []):
        try:
            if not isinstance(signature, dict):
                continue
            header = json.loads(unb64(signature["protected"]))
            if not isinstance(header, dict):
                continue
            if header.get("alg") != "EdDSA" or header.get("crit") or "jku" in header:
                continue
            key = trusted_keys[header["kid"]]
            key.verify(
                unb64(signature["signature"]),
                (signature["protected"] + "." + b64(jcs.canonicalize(unsigned))).encode(),
            )
            return unsigned
        except (KeyError, ValueError, TypeError, InvalidSignature):
            continue
    raise ValueError("No signature from a trusted key verified.")


def webhook_headers(
    body: bytes, secret: bytes, nonce: str, now: int | None = None
) -> dict[str, str]:
    timestamp = str(int(time.time()) if now is None else now)
    digest = hmac.new(
        secret, timestamp.encode() + b"." + nonce.encode() + b"." + body, hashlib.sha256
    ).hexdigest()
    return {
        "x-maplewood-time": timestamp,
        "x-maplewood-nonce": nonce,
        "x-maplewood-signature": digest,
    }


def verify_webhook(
    body: bytes, headers: dict, secret: bytes, seen: dict[str, int], now: int | None = None
) -> None:
    current = int(time.time()) if now is None else now
    stamp = int(headers.get("x-maplewood-time", "0"))
    nonce = headers.get("x-maplewood-nonce", "")
    for old in [key for key, expiry in seen.items() if expiry < current]:
        del seen[old]
    expected = webhook_headers(body, secret, nonce, stamp)["x-maplewood-signature"]
    if (
        abs(current - stamp) > 300
        or not nonce
        or nonce in seen
        or not hmac.compare_digest(expected, headers.get("x-maplewood-signature", ""))
    ):
        raise ValueError("Unverified, expired or replayed webhook.")
    seen[nonce] = current + 300
