# Why this works

Cross the official A2A adapter into LangGraph and the private MCP kitchen. Preserve state and produce only validated artifacts.

The exercise uses real framework objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from common.protocol import as_dict, request

    response = await context["http"].post(
        context["path"],
        json=as_dict(
            request(
                context["brief"],
                task_id=context.get("task_id", ""),
                context_id=context.get("context_id", ""),
            )
        ),
    )
    return response.text if context["path"].endswith("stream") else response.json()
~~~
