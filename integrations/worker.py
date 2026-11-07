"""Isolated framework runtime. Input and output are JSON; external networking is blocked."""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["DO_NOT_TRACK"] = "1"

from agents.business import quote  # noqa: E402


async def adk(vendor, brief):
    from google.adk.agents import BaseAgent
    from google.adk.events import Event
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    class InventoryAgent(BaseAgent):
        async def _run_async_impl(self, ctx):
            result = quote(vendor, ctx.session.state["brief"])
            yield Event(
                author=self.name,
                content=types.Content(role="model", parts=[types.Part(text=json.dumps(result))]),
            )

    runner = InMemoryRunner(agent=InventoryAgent(name="maplewood_inventory"), app_name="maplewood")
    try:
        await runner.session_service.create_session(
            app_name="maplewood", user_id="fixture", session_id="fixture", state={"brief": brief}
        )
        events = [
            event
            async for event in runner.run_async(
                user_id="fixture",
                session_id="fixture",
                new_message=types.Content(
                    role="user", parts=[types.Part(text="Quote the supplied inventory brief.")]
                ),
            )
        ]
        text = next(event.content.parts[0].text for event in reversed(events) if event.content)
        return json.loads(text)
    finally:
        await runner.close()


async def pydantic(vendor, brief):
    from pydantic_ai import Agent
    from pydantic_ai.messages import ModelResponse, TextPart
    from pydantic_ai.models.function import FunctionModel

    def scripted_model(messages, info):
        return ModelResponse(parts=[TextPart(json.dumps(quote(vendor, brief)))])

    agent = Agent(FunctionModel(scripted_model), output_type=str)
    result = await agent.run("Return the synthetic inventory quote.")
    return json.loads(result.output)


async def strands(vendor, brief):
    from strands import Agent
    from strands.models import Model

    class FixtureModel(Model):
        def update_config(self, **config):
            self.config = config

        def get_config(self):
            return {"model_id": "maplewood-scripted"}

        async def structured_output(self, output_model, prompt, **kwargs):
            yield {"output": output_model.model_validate(quote(vendor, brief))}

        async def stream(self, messages, *args, **kwargs):
            yield {"messageStart": {"role": "assistant"}}
            yield {
                "contentBlockDelta": {
                    "contentBlockIndex": 0,
                    "delta": {"text": json.dumps(quote(vendor, brief))},
                }
            }
            yield {"contentBlockStop": {"contentBlockIndex": 0}}
            yield {"messageStop": {"stopReason": "end_turn"}}
            yield {
                "metadata": {
                    "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
                    "metrics": {"latencyMs": 0},
                }
            }

    agent = Agent(model=FixtureModel(), callback_handler=None)
    return json.loads(str(await agent.invoke_async("Quote the synthetic event.")))


async def crewai(vendor, brief):
    from crewai import Agent, BaseLLM, Crew, Task

    class FixtureLLM(BaseLLM):
        def call(self, messages, tools=None, callbacks=None, available_functions=None, **kwargs):
            return "Final Answer: " + json.dumps(quote(vendor, brief))

        def supports_function_calling(self):
            return False

    agent = Agent(
        role="Maplewood inventory planner",
        goal="Return a validated synthetic quote.",
        backstory="You quote inventory without booking anything.",
        llm=FixtureLLM(model="maplewood-scripted"),
        allow_delegation=False,
        verbose=False,
        max_iter=2,
    )
    task = Task(
        description="Quote the supplied synthetic event.",
        expected_output="A JSON quote.",
        agent=agent,
    )
    result = await Crew(agents=[agent], tasks=[task], verbose=False, memory=False).kickoff_async()
    return json.loads(result.raw)


async def microsoft(vendor, brief):
    from agent_framework import WorkflowBuilder, WorkflowContext, executor

    @executor
    async def inventory(payload: dict, ctx: WorkflowContext[dict]):
        await ctx.yield_output(quote(vendor, payload))

    workflow = WorkflowBuilder(start_executor=inventory).build()
    result = await workflow.run(brief)
    return result.get_outputs()[0]


async def beeai(vendor, brief):
    from beeai_framework.workflows.workflow import Workflow
    from pydantic import BaseModel, Field

    class State(BaseModel):
        brief: dict
        quote: dict = Field(default_factory=dict)

    async def inventory(state):
        state.quote = quote(vendor, state.brief)
        return Workflow.END

    workflow = Workflow(State).add_step("inventory", inventory)
    result = await workflow.run(State(brief=brief))
    return result.state.quote


async def main():
    payload = json.loads(sys.stdin.readline())
    runtimes = {
        "adk": adk,
        "pydantic": pydantic,
        "strands": strands,
        "crewai": crewai,
        "microsoft": microsoft,
        "beeai": beeai,
    }
    result = await runtimes[payload["framework"]](payload["vendor"], payload["brief"])
    print("@@MAPLEWOOD_RESULT@@" + json.dumps(result), flush=True)


if __name__ == "__main__":
    import pytest_socket

    class OfflinePolicy(type(asyncio.get_event_loop_policy())):
        def new_event_loop(self):
            # Some frameworks create loops in worker threads. Permit only their
            # construction here, then restore the network guard before work runs.
            pytest_socket.enable_socket()
            try:
                return super().new_event_loop()
            finally:
                pytest_socket.disable_socket()

    asyncio.set_event_loop_policy(OfflinePolicy())
    loop = asyncio.new_event_loop()
    pytest_socket.disable_socket()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(loop.shutdown_default_executor())
        loop.close()
