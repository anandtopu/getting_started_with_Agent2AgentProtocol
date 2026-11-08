"""Automated card-key rotation with overlap and an HTTPS-pinned JWKS endpoint."""

import time
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from starlette.responses import JSONResponse
from starlette.routing import Route

from common.card_trust import jwks
from common.protocol import as_dict
from common.security import sign_card


class RotatingCardKeys:
    def __init__(self, identity, *, interval=300, overlap=90, clock=time.monotonic):
        if interval < 1 or overlap < 30:
            raise ValueError("Rotation interval must be positive; overlap must cover card caching")
        self.identity, self.interval, self.overlap, self.clock = identity, interval, overlap, clock
        self.keys, self.current, self.next_rotation = {}, None, float("-inf")

    def rotate(self):
        now = self.clock()
        if now >= self.next_rotation:
            if self.current in self.keys:
                key, _ = self.keys[self.current]
                self.keys[self.current] = (key, now + self.overlap)
            self.current = "maplewood-" + uuid4().hex
            self.keys[self.current] = (Ed25519PrivateKey.generate(), float("inf"))
            self.next_rotation = now + self.interval
        self.keys = {kid: pair for kid, pair in self.keys.items() if pair[1] > now}

    def card(self):
        self.rotate()
        return sign_card(as_dict(self.identity), self.keys[self.current][0], self.current)

    def public_keys(self):
        self.rotate()
        return {
            "keys": [jwks(key.public_key(), kid)["keys"][0] for kid, (key, _) in self.keys.items()]
        }

    def revoke(self, kid):
        self.keys.pop(kid, None)
        if kid == self.current:
            self.next_rotation = float("-inf")

    def routes(self):
        async def card(request):
            return JSONResponse(self.card())

        async def keys(request):
            return JSONResponse(self.public_keys())

        return [Route("/.well-known/agent-card.json", card), Route("/.well-known/jwks.json", keys)]
