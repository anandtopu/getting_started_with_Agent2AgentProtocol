"""Bound authenticated request bursts without retaining unbounded identity state."""

import time


class RateBudget:
    def __init__(self, limit=120, window=60, max_identities=10_000, clock=time.monotonic):
        self.limit, self.window, self.max_identities, self.clock = (
            limit,
            window,
            max_identities,
            clock,
        )
        self.buckets = {}

    def allow(self, identity: str) -> bool:
        now = self.clock()
        started, count = self.buckets.get(identity, (now, 0))
        if now - started >= self.window:
            started, count = now, 0
        if identity not in self.buckets and len(self.buckets) >= self.max_identities:
            self.buckets = {
                key: value for key, value in self.buckets.items() if now - value[0] < self.window
            }
            if len(self.buckets) >= self.max_identities:
                return False
        if count >= self.limit:
            return False
        self.buckets[identity] = (started, count + 1)
        return True
