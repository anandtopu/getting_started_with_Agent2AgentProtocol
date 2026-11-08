"""One lifecycle adapter; each framework executes its own internal workflow."""

from agents.business import quote
from agents.executor import VendorExecutor
from common.frameworks import framework_quote


class FrameworkVendor(VendorExecutor):
    def __init__(self, vendor: str, framework: str):
        super().__init__(vendor)
        self.framework = framework

    async def produce_quote(self, brief, *, partner=False):
        expected = quote(self.vendor, brief, partner=partner)
        try:
            result = await framework_quote(self.framework, self.vendor, brief, partner=partner)
        except ValueError as exc:
            raise RuntimeError("Framework worker unavailable or invalid") from exc
        if result != expected:
            raise RuntimeError("Framework quote did not match the inventory contract")
        return result
