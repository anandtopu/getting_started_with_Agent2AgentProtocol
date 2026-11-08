# Why this works

Consume actual provider framing, validate the final tool name and argument schema, and reject incomplete or unsafe output.

The exercise uses real native_model objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from jsonschema import ValidationError

    try:
        return await context["model"].tool_decide("Select a safe menu action.", context["schema"])
    except (ValueError, ValidationError):
        return {"rejected": True}
~~~
