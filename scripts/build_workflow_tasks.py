"""Distinct workflow exercises using real A2A/MCP routes and provider wire frames."""

from scripts.build_advanced_tasks import TASKS, add, main

TASKS.clear()

for action in ("send", "get", "missing", "parse", "method", "rejected"):
    add(
        "03",
        "manual",
        action,
        f"Inspect the hand-built server: {action}",
        """
response = await context['http'].post('/rpc', **context['arguments'])
return response.json()
""",
        f"Send the supplied {action} envelope and return the server's response. Explain RPC failures versus business rejection.",
        "conformance",
    )

for provider in ("ollama", "openai", "anthropic", "gemini", "truncated", "unsafe"):
    add(
        "09",
        "native_model",
        provider,
        f"Validate native tool frames: {provider}",
        """
from jsonschema import ValidationError
try:
    return await context['model'].tool_decide('Select a safe menu action.', context['schema'])
except (ValueError, ValidationError):
    return {'rejected': True}
""",
        "Consume actual provider framing, validate the final tool name and argument schema, and reject incomplete or unsafe output.",
        "secure" if provider in {"unsafe", "truncated"} else "interop",
    )

for action in ("parallel", "resume", "untrusted", "private", "rejected", "fallback"):
    add(
        "10",
        "orchestration",
        action,
        f"Coordinate vendor work: {action}",
        """
from agents.concierge import Concierge
try:
    return await Concierge(context['clients'], model=context.get('model'),
        fallbacks=context.get('fallbacks')).plan(context['brief'], context.get('previous'))
except ValueError:
    return {'rejected_selection': True}
""",
        "Use only provisioned vendor clients, preserve paused IDs, inspect every delegation, and require approval. The grader varies vendors, missing inputs, and failure modes.",
        "secure" if action in {"private", "untrusted"} else "build",
    )

for action in ("quote", "pause", "resume", "unsafe", "capacity", "stream"):
    code = """
from common.protocol import as_dict, request
response = await context['http'].post(context['path'], json=as_dict(request(
    context['brief'], task_id=context.get('task_id', ''), context_id=context.get('context_id', ''))))
return response.text if context['path'].endswith('stream') else response.json()
"""
    add(
        "11",
        "framework",
        action,
        f"Wrap a real LangGraph workflow: {action}",
        code,
        "Cross the official A2A adapter into LangGraph and the private MCP kitchen. Preserve state and produce only validated artifacts.",
        "interop",
    )

for action in ("capacity", "too_many", "invalid", "quote", "pause", "reject"):
    code = (
        """
from agents.kitchen import check_kitchen
try:
    return await check_kitchen(context['guests'])
except ValueError:
    return {'rejected': True}
"""
        if action in {"capacity", "too_many", "invalid"}
        else """
from common.protocol import as_dict, request
return (await context['http'].post('/message:send', json=as_dict(request(context['brief'])))).json()
"""
    )
    add(
        "12",
        "mcp",
        action,
        f"Keep kitchen tools inside the vendor: {action}",
        code,
        "Call the real MCP server in memory or its A2A wrapper. Capacity failures must not become fabricated quotes.",
        "interop",
    )

for action in ("private_ip", "unlisted", "redirect", "oversize", "valid", "replay"):
    code = (
        """
from common.security import fetch_file
try:
    return await fetch_file(context['url'], context['allowed'], context['http'], limit=64)
except ValueError:
    return None
"""
        if action != "replay"
        else """
from common.security import verify_webhook
seen = {}
verify_webhook(context['body'], context['headers'], context['secret'], seen, now=100)
try:
    verify_webhook(context['body'], context['headers'], context['secret'], seen, now=100)
    return False
except ValueError:
    return True
"""
    )
    add(
        "15",
        "egress",
        action,
        f"Defend a real I/O boundary: {action}",
        code,
        "Enforce explicit destinations, public addresses, byte limits and replay protection before accepting external data.",
        "secure",
    )

if __name__ == "__main__":
    main()
