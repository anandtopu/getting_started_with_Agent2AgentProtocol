"""The no-SDK microscope distinguishes RPC failures from declined business work."""

import httpx

from common.manual_server import manual_app


async def test_manual_envelope():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=manual_app()), base_url="http://manual.test"
    ) as http:
        assert (await http.post("/rpc", content="{")).json()["error"]["code"] == -32700
        envelope = {"jsonrpc": "2.0", "id": "client-1", "method": "Other", "params": {}}
        assert (await http.post("/rpc", json=envelope)).json()["error"]["code"] == -32601
        envelope["method"] = "SendMessage"
        assert (await http.post("/rpc", json=envelope)).json()["error"]["code"] == -32602
        envelope["params"] = {
            "message": {"messageId": "m1", "role": "ROLE_USER", "parts": [{"data": {"guests": 40}}]}
        }
        result = (await http.post("/rpc", json=envelope)).json()
        assert result["id"] == "client-1"
        assert result["result"]["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
        envelope["params"]["message"]["parts"][0]["data"]["guests"] = 150
        result = (await http.post("/rpc", json=envelope)).json()
        assert result["result"]["task"]["status"]["state"] == "TASK_STATE_REJECTED"
        envelope["params"]["message"]["parts"][0]["data"]["guests"] = {}
        assert (await http.post("/rpc", json=envelope)).json()["result"]["task"]["status"][
            "state"
        ] == "TASK_STATE_REJECTED"
