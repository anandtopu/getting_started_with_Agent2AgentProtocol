"""Teach tool calling as a validated request for a function, with a fixed step limit."""

from agents.business import quote


async def catering_agent(model, brief: dict) -> dict:
    for _ in range(3):
        decision = await model.decide(f"Choose ask_dietary or quote_menu. Event data: {brief}")
        if decision.get("tool") == "ask_dietary":
            return {"state": "TASK_STATE_INPUT_REQUIRED", "question": "Provide dietary counts."}
        if decision.get("tool") == "quote_menu":
            return {"state": "TASK_STATE_COMPLETED", "quote": quote("catering", brief)}
    raise ValueError("Model exceeded the three-step tool budget.")
