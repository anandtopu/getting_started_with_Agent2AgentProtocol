from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    from a2a.client import ClientConfig, create_client
    from a2a.types import AgentCard
    from google.protobuf.json_format import ParseDict

    card = ParseDict((await http.get("/.well-known/agent-card.json")).json(), AgentCard())
    sdk = await create_client(card, ClientConfig(httpx_client=http, streaming=False))
    result = [as_dict(item) async for item in sdk.send_message(request(brief))][-1]
    return result["task"]
