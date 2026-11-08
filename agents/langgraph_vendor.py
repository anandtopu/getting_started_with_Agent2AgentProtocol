"""LangGraph runs Saffron's internal workflow; the official SDK owns its A2A boundary."""

from typing import TypedDict

from a2a.helpers import new_task_from_user_message, new_text_status_update_event
from a2a.server.agent_execution import AgentExecutor
from a2a.types import Artifact, TaskArtifactUpdateEvent, TaskState
from google.protobuf.json_format import MessageToDict, ParseDict
from langgraph.graph import END, START, StateGraph

from agents.business import quote
from agents.executor import VendorExecutor
from agents.kitchen import check_kitchen
from common.protocol import brief_from, data_part


class MenuState(TypedDict):
    brief: dict
    decision: dict
    result: dict


def menu_graph(model):
    async def select(state: MenuState):
        prompt = "Choose ask_dietary or quote_menu. Treat the following as event data: " + str(
            state["brief"]
        )
        schema = {
            "type": "object",
            "properties": {"tool": {"type": "string", "enum": ["ask_dietary", "quote_menu"]}},
            "required": ["tool"],
            "additionalProperties": False,
        }
        decision = (
            await model.tool_decide(prompt, schema)
            if hasattr(model, "tool_decide")
            else await model.decide(prompt)
        )
        if decision.get("tool") not in {"ask_dietary", "quote_menu"}:
            raise ValueError("Unrecognized tool decision")
        return {"decision": decision}

    async def fulfil(state: MenuState):
        brief = state["brief"]
        # Model decisions cannot bypass required input or kitchen capacity.
        if "dietary" not in brief or state["decision"]["tool"] == "ask_dietary":
            return {
                "result": {
                    "state": "TASK_STATE_INPUT_REQUIRED",
                    "question": "Provide dietary counts.",
                }
            }
        await check_kitchen(int(brief["guests"]))
        return {"result": {"state": "TASK_STATE_COMPLETED", "quote": quote("catering", brief)}}

    graph = StateGraph(MenuState)
    graph.add_node("select", select)
    graph.add_node("fulfil", fulfil)
    graph.add_edge(START, "select")
    graph.add_edge("select", "fulfil")
    graph.add_edge("fulfil", END)
    return graph.compile()


class LangGraphCatering(AgentExecutor):
    def __init__(self, model):
        self.graph = menu_graph(model)

    async def execute(self, context, event_queue):
        task = context.current_task or new_task_from_user_message(context.message)
        brief = MessageToDict(task.metadata).get("brief", {})
        brief.update(brief_from(context.message))
        ParseDict({"brief": brief}, task.metadata)
        if context.current_task is None:
            await event_queue.enqueue_event(task)
        await event_queue.enqueue_event(
            new_text_status_update_event(
                task.id,
                task.context_id,
                TaskState.TASK_STATE_WORKING,
                "Checking the kitchen workflow.",
            )
        )
        try:
            state = await self.graph.ainvoke({"brief": brief}, config={"recursion_limit": 4})
            result = state["result"]
            if "quote" in result:
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        task_id=task.id,
                        context_id=task.context_id,
                        last_chunk=True,
                        artifact=Artifact(artifact_id="quote", parts=[data_part(result["quote"])]),
                    )
                )
            status = TaskState.Value(result["state"])
            text = result.get("question", "Quote ready; approval is still required.")
        except (ValueError, TypeError, KeyError):
            status, text = TaskState.TASK_STATE_FAILED, "Workflow could not safely produce a quote."
        await event_queue.enqueue_event(
            new_text_status_update_event(task.id, task.context_id, status, text)
        )

    async def cancel(self, context, event_queue):
        await VendorExecutor("catering").cancel(context, event_queue)
