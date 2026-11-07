"""A deliberately small JSON-RPC subset, written without importing an A2A SDK.

This first-lesson microscope implements SendMessage only. Later lessons use the
official SDK for the complete lifecycle, conformance, persistence and security.
"""

from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from agents.business import quote


def manual_app():
    app = FastAPI()

    @app.post("/rpc")
    async def rpc(incoming: Request):
        try:
            body = await incoming.json()
        except ValueError:
            return JSONResponse(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            )
        identifier = body.get("id") if isinstance(body, dict) else None

        def error(code, message):
            return JSONResponse(
                {"jsonrpc": "2.0", "id": identifier, "error": {"code": code, "message": message}}
            )

        if not isinstance(body, dict) or body.get("jsonrpc") != "2.0" or "id" not in body:
            return error(-32600, "Invalid request")
        if body.get("method") != "SendMessage":
            return error(-32601, "Method not found")
        try:
            message = body["params"]["message"]
            if message["role"] != "ROLE_USER" or not message["messageId"]:
                raise ValueError("A user message and messageId are required")
            if message.get("taskId"):
                return error(-32001, "Task not found")
            brief = next(part["data"] for part in message["parts"] if "data" in part)
            if not isinstance(brief, dict):
                raise ValueError("Expected an event brief object")
        except (KeyError, TypeError, ValueError, StopIteration):
            return error(-32602, "Invalid params")
        task = {"id": str(uuid4()), "contextId": message.get("contextId") or str(uuid4())}
        try:
            result = quote("venues", brief)
            task["status"] = {"state": "TASK_STATE_COMPLETED"}
            task["artifacts"] = [
                {
                    "artifactId": "quote",
                    "parts": [{"data": result, "mediaType": "application/json"}],
                }
            ]
        except ValueError:
            task["status"] = {"state": "TASK_STATE_REJECTED"}
        # KEY IDEA: RPC id correlates the exchange; task id identifies the work.
        return {"jsonrpc": "2.0", "id": identifier, "result": {"task": task}}

    return app
