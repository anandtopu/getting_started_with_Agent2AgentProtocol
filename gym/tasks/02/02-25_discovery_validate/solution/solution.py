async def exercise(http, brief, previous):
    from a2a.types import AgentCard
    from google.protobuf.json_format import ParseDict

    document = (await http.get("/.well-known/agent-card.json")).json()
    parsed = ParseDict(document, AgentCard())
    return {"name": parsed.name, "version": parsed.version}
