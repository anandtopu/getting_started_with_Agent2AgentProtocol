"""Maplewood Control Room. Run: uv run streamlit run control_room/app.py."""

import json

import grpc
import httpx
import streamlit as st
from a2a.types.a2a_pb2_grpc import A2AServiceStub

from common.config import ROOT, VENDORS, grpc_target, url
from common.protocol import as_dict, request

st.set_page_config(page_title="Maplewood Control Room", page_icon="🍁", layout="wide")
st.title("Maplewood Events")
st.caption("Discover vendors, inspect their contracts and watch work arrive.")
vendor = st.selectbox("Vendor", VENDORS)
state_file = ROOT / "workspace/network.json"
tokens = json.loads(state_file.read_text()).get("tokens", {}) if state_file.exists() else {}
headers = {"Authorization": "Bearer " + tokens.get(vendor, ""), "A2A-Version": "1.0"}
brief = st.text_area(
    "Event brief (JSON)", '{"guests":40,"date":"2027-06-01","dietary":{"vegan":10,"standard":30}}'
)
streaming = st.checkbox("Watch streamed events", value=True)
left, right = st.columns(2)

if left.button("Discover"):
    try:
        response = httpx.get(url(vendor) + "/.well-known/agent-card.json", timeout=5)
        response.raise_for_status()
        st.session_state["card"] = response.json()
    except httpx.HTTPError:
        st.error("Start the local network: uv run python scripts/network.py up --module 08")
if "card" in st.session_state:
    with st.expander("Agent Card", expanded=True):
        st.json(st.session_state["card"])

if right.button("Send brief"):
    try:
        payload = as_dict(request(json.loads(brief)))
        with httpx.Client(base_url=url(vendor), headers=headers, timeout=30) as client:
            if vendor == "print":
                with grpc.insecure_channel(grpc_target()) as channel:
                    stub = A2AServiceStub(channel)
                    metadata = (("authorization", headers["Authorization"]), ("a2a-version", "1.0"))
                    message = request(json.loads(brief))
                    if streaming:
                        for event in stub.SendStreamingMessage(
                            message, metadata=metadata, timeout=30
                        ):
                            st.json(as_dict(event))
                    else:
                        st.json(as_dict(stub.SendMessage(message, metadata=metadata, timeout=30)))
            elif streaming:
                with client.stream("POST", "/message:stream", json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            st.json(json.loads(line[6:]))
            else:
                response = client.post("/message:send", json=payload)
                response.raise_for_status()
                st.json(response.json())
    except (httpx.HTTPError, grpc.RpcError, ValueError) as exc:
        st.error(f"Unable to complete the request: {exc}. Check scripts/check_env.py.")

with st.expander("Live verified webhook deliveries", expanded=True):
    st.caption("Start: uv run python scripts/webhook_lab.py. This inbox persists across restarts.")
    folder = ROOT / "workspace/webhook-lab"
    if (folder / "credentials.json").exists():
        if st.button("Request a catering quote with push updates"):
            settings = json.loads((folder / "credentials.json").read_text())
            payload = as_dict(request(json.loads(brief)))
            payload["configuration"] = {
                "taskPushNotificationConfig": {
                    "id": "control-room",
                    "url": "http://127.0.0.1:8190/notifications",
                }
            }
            try:
                response = httpx.post(
                    "http://127.0.0.1:8161/message:send",
                    json=payload,
                    headers={"Authorization": "Bearer " + settings["token"], "A2A-Version": "1.0"},
                    timeout=30,
                )
                response.raise_for_status()
                st.json(response.json())
            except httpx.HTTPError:
                st.error("The callback lab is not reachable. Start it in another terminal.")
        st.button("Refresh verified inbox")
        if (folder / "inbox.sqlite").exists():
            import sqlite3

            with sqlite3.connect(
                (folder / "inbox.sqlite").as_uri() + "?mode=ro", uri=True
            ) as database:
                for row in database.execute("SELECT body FROM inbox ORDER BY rowid DESC LIMIT 30"):
                    st.json(json.loads(row[0]))
