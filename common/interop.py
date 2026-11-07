"""Compare one business contract across three official SDK bindings."""

from common.protocol import as_dict, request
from common.testing import InProcessGrpc, client


async def interop_lab():
    brief = {"guests": 40, "date": "2027-06-01"}
    results = {}
    async with client("venues") as vendor:
        rest = await vendor.post("/message:send", json=as_dict(request(brief)))
        rpc = await vendor.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": "interop",
                "method": "SendMessage",
                "params": as_dict(request(brief)),
            },
        )
        results["HTTP+JSON"] = rest.json()["task"]
        results["JSONRPC"] = rpc.json()["result"]["task"]
    grpc = InProcessGrpc("venues")
    try:
        results["GRPC"] = as_dict(await grpc.unary("SendMessage", request(brief)))["task"]
    finally:
        await grpc.service.request_handler.aclose()
    normalized = {
        name: {"state": task["status"]["state"], "quote": task["artifacts"][0]["parts"][0]["data"]}
        for name, task in results.items()
    }
    return {
        "bindings": normalized,
        "equivalent": all(value == normalized["JSONRPC"] for value in normalized.values()),
    }
