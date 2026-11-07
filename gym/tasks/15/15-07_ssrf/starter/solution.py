async def fetch(url, allowed, client):
    # YOUR CODE HERE: allow-list membership alone is not enough.
    response = await client.get(url)
    return response.content
