"""Bound peer responses by decoded bytes and total elapsed time, including headers."""

import asyncio
import json

import httpx


async def response_bytes(response, limit: int) -> bytes:
    content = bytearray()
    async for chunk in response.aiter_bytes():
        if len(chunk) > limit - len(content):
            raise ValueError("Peer response exceeds size limit.")
        content.extend(chunk)
    return bytes(content)


async def request_json(client, method, url, *, timeout=5, limit=1_000_000, **kwargs):
    try:
        async with asyncio.timeout(timeout):
            async with client.stream(
                method, url, follow_redirects=False, timeout=timeout, **kwargs
            ) as response:
                response.raise_for_status()
                return json.loads(await response_bytes(response, limit))
    except TimeoutError as exc:
        raise httpx.ReadTimeout("Peer response exceeded total time limit.") from exc
