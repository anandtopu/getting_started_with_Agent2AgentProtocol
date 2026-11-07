"""Streaming and push notifications: stream.

Concepts: Read SSE frames, Assemble artifact chunks, Verify a push delivery.
Spec: https://a2a-protocol.org/v1.0.1/specification/; protobuf: https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto.
Run: uv run python modules/07_streaming_push/use_case/run.py
Agents: in-process; no separately running services. LLM: no (scripted when needed).
Expected: corresponding wire/*.result.json; IDs and timestamps vary.
"""

import asyncio

from common.lessons import experiment
from common.pretty import show


async def main() -> None:
    # KEY IDEA: observe the actual result at this protocol boundary.
    show(await experiment("stream"))


if __name__ == "__main__":
    asyncio.run(main())
