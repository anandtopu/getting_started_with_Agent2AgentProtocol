"""Your first A2A client: sdk_client.

Concepts: Create an SDK client, Handle protocol errors, Separate safe retries from side effects.
Spec: https://a2a-protocol.org/v1.0.1/specification/; protobuf: https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto.
Run: uv run python modules/04_first_client/use_case/run.py
Agents: in-process; no separately running services. LLM: no (scripted when needed).
Expected: corresponding wire/*.result.json; IDs and timestamps vary.
"""

import asyncio

from common.lessons import experiment
from common.pretty import show


async def main() -> None:
    # KEY IDEA: observe the actual result at this protocol boundary.
    show(await experiment("sdk_client"))


if __name__ == "__main__":
    asyncio.run(main())
