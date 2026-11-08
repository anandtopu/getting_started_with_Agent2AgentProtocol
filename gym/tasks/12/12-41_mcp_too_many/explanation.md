# Why this works

Call the real MCP server in memory or its A2A wrapper. Capacity failures must not become fabricated quotes.

The exercise uses real mcp objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from agents.kitchen import check_kitchen

    try:
        return await check_kitchen(context["guests"])
    except ValueError:
        return {"rejected": True}
~~~
