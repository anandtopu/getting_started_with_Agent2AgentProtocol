# Why this works

Use only provisioned vendor clients, preserve paused IDs, inspect every delegation, and require approval. The grader varies vendors, missing inputs, and failure modes.

The exercise uses real orchestration objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from agents.concierge import Concierge

    try:
        return await Concierge(
            context["clients"], model=context.get("model"), fallbacks=context.get("fallbacks")
        ).plan(context["brief"], context.get("previous"))
    except ValueError:
        return {"rejected_selection": True}
~~~
