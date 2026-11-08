async def exercise(context):
    from jsonschema import ValidationError

    try:
        return await context["model"].tool_decide("Select a safe menu action.", context["schema"])
    except (ValueError, ValidationError):
        return {"rejected": True}
