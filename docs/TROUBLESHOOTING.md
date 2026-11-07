# Troubleshooting

| Symptom | Check and remedy |
|---|---|
| Port already in use | Run scripts/check_env.py, then network.py down in this repository. Stop only the process you own. |
| Windows firewall warning | Local examples bind to loopback. Do not expose a demo on public interfaces to fix a local connection problem. |
| Card returns 404 | Use /.well-known/agent-card.json at the advertised server base URL. |
| Version mismatch | Send A2A-Version: 1.0 and verify the selected interface's protocolVersion. |
| HTTP 401 | Obtain the vendor credential outside the protocol. The launcher writes local tokens under ignored workspace/. |
| Partner card returns 403 | A valid basic token does not grant partner scope. |
| Stream appears all at once | The teaching recorder buffers for inspection. Use the Control Room or a streaming client for arrival timing; disable buffering in production proxies. |
| Stream stalls behind a proxy | Check idle timeouts, SSE content type and buffering; compare direct loopback behavior. |
| Callback cannot reach localhost | A remote server cannot call your computer's loopback address. The offline lab uses ASGI transport; deployment needs an approved reachable receiver. |
| gRPC generation fails on Windows | Use the installed grpcio-tools through Python and the versioned proto; do not assume a system protoc is present. |
| Docker cannot connect | Start your Docker-compatible engine and select its context before running Compose. |
| Keycloak token rejected | Check issuer, audience, expiration and realm/client configuration; do not disable signature checks. |
| Notebook reports an event loop already running | Use top-level await in notebook cells; do not call asyncio.run inside Jupyter. |
| Offline install fails | Initial dependency installation needs network access; offline execution assumes cached locked packages. |
| Model unavailable | Check .env, provider keys, model access and local Ollama; graded tasks need none of these. |
| Encoding error in a Windows terminal | Use an UTF-8 terminal or Python UTF-8 mode. Essential commands print ASCII status messages. |
| Gym reports unexpected success | A starter must fail before the learner repairs it. Run validate_gym and inspect task.json acceptance cases. |

SDK shutdown may log a dispatcher cleanup warning after a short in-process run.
Check the captured final event and test outcome; do not ignore missing terminal
states or failed assertions.
