from common.security import fetch_file


async def fetch(url, allowed, client):
    return await fetch_file(url, allowed, client)
