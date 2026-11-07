"""Capture every normative operation using the official JSON-RPC and gRPC handlers."""

import asyncio
import json

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.request_handlers.grpc_handler import GrpcHandler
from a2a.server.tasks import InMemoryPushNotificationConfigStore, InMemoryTaskStore
from a2a.types import a2a_pb2 as pb
from google.protobuf.json_format import ParseDict

from agents.catalog import card
from agents.executor import VendorExecutor
from common.config import ROOT
from common.protocol import as_dict, request
from common.testing import ServiceContext, client


def handler():
    identity = card("catering")
    identity.capabilities.push_notifications = True
    identity.capabilities.extended_agent_card = True

    async def permitted(url):
        return url == "https://callback.maplewood.example/notify"

    result = DefaultRequestHandler(
        VendorExecutor("catering"),
        InMemoryTaskStore(),
        identity,
        extended_agent_card=identity,
        push_config_store=InMemoryPushNotificationConfigStore(),
        push_url_validator=permitted,
    )
    result.course_card = identity
    return result


async def capture(binding):
    records = []
    active = handler()
    service = GrpcHandler(active)
    async with client("catering", handler=active, partner=True, records=records) as http:

        async def invoke(name, params):
            descriptor = pb.DESCRIPTOR.services_by_name["A2AService"].methods_by_name[name]
            if binding == "HTTP_JSON":
                task = params.get("taskId", params.get("id", ""))
                routes = {
                    "SendMessage": ("POST", "/message:send"),
                    "SendStreamingMessage": ("POST", "/message:stream"),
                    "GetTask": ("GET", f"/tasks/{task}"),
                    "ListTasks": ("GET", "/tasks"),
                    "CancelTask": ("POST", f"/tasks/{task}:cancel"),
                    "SubscribeToTask": ("GET", f"/tasks/{task}:subscribe"),
                    "CreateTaskPushNotificationConfig": (
                        "POST",
                        f"/tasks/{task}/pushNotificationConfigs",
                    ),
                    "GetTaskPushNotificationConfig": (
                        "GET",
                        f"/tasks/{task}/pushNotificationConfigs/{params.get('id')}",
                    ),
                    "ListTaskPushNotificationConfigs": (
                        "GET",
                        f"/tasks/{task}/pushNotificationConfigs",
                    ),
                    "DeleteTaskPushNotificationConfig": (
                        "DELETE",
                        f"/tasks/{task}/pushNotificationConfigs/{params.get('id')}",
                    ),
                    "GetExtendedAgentCard": ("GET", "/extendedAgentCard"),
                }
                method, path = routes[name]
                options = (
                    {"json": params}
                    if method == "POST"
                    else {
                        "params": {
                            k: str(v).lower() if isinstance(v, bool) else v
                            for k, v in params.items()
                            if k not in {"id", "taskId"}
                        }
                    }
                )
                response = await http.request(method, path, **options)
                try:
                    return response.json()
                except ValueError:
                    return response.text
            if binding == "JSONRPC":
                response = await http.post(
                    "/rpc", json={"jsonrpc": "2.0", "id": name, "method": name, "params": params}
                )
                try:
                    result = response.json()
                except ValueError:
                    result = response.text
                return result.get("result", result) if isinstance(result, dict) else result
            message = ParseDict(params, getattr(pb, descriptor.input_type.name)())
            try:
                if descriptor.server_streaming:
                    result = [
                        as_dict(item)
                        async for item in getattr(service, name)(message, ServiceContext())
                    ]
                else:
                    result = as_dict(await getattr(service, name)(message, ServiceContext()))
            except RuntimeError as exc:
                result = {"error": str(exc)}
            records.append(
                {
                    "binding": "gRPC service boundary",
                    "operation": name,
                    "request": as_dict(message),
                    "response": result,
                    "request_hex": message.SerializeToString().hex(),
                }
            )
            return result

        first = await invoke("SendMessage", as_dict(request({"guests": 40})))
        task_id = first["task"]["id"]
        await invoke("GetTask", {"id": task_id, "historyLength": 1})
        await invoke("ListTasks", {"pageSize": 1, "includeArtifacts": True})
        await invoke(
            "CreateTaskPushNotificationConfig",
            {
                "taskId": task_id,
                "id": "capture",
                "url": "https://callback.maplewood.example/notify",
            },
        )
        await invoke("GetTaskPushNotificationConfig", {"taskId": task_id, "id": "capture"})
        await invoke("ListTaskPushNotificationConfigs", {"taskId": task_id})
        await invoke("DeleteTaskPushNotificationConfig", {"taskId": task_id, "id": "capture"})
        await invoke("GetExtendedAgentCard", {})
        await invoke("CancelTask", {"id": task_id})
        # A terminal task cannot be subscribed to; capture the real error as well.
        await asyncio.wait_for(invoke("SubscribeToTask", {"id": task_id}), timeout=5)
        await invoke(
            "SendStreamingMessage", as_dict(request({"guests": 40, "dietary": {"vegan": 40}}))
        )
    path = ROOT / "docs/wire" / (binding.lower() + "-operations.jsonl")
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return len(records)


async def main():
    for binding in ["JSONRPC", "HTTP_JSON", "GRPC"]:
        print(binding, await capture(binding), "captured operations")


if __name__ == "__main__":
    asyncio.run(main())
