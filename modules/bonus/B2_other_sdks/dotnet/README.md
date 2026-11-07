# Native .NET venue agent — preview SDK

This optional experiment uses the official A2A.AspNetCore **1.0.0-preview4**.
Upstream has not published a stable 1.0 release. Do not mistake its protocol
version (1.0) for the maturity of the SDK package.

Install the .NET 10 SDK, then from the repository root:

~~~console
uv run python scripts/check_dotnet_interop.py
~~~

For a private SDK installation, pass --dotnet with the path to its executable.
The checker restores the committed dependency lock, compiles the server, starts
it on 127.0.0.1:8402 with a fresh token, and checks real Python-to-.NET requests.
It compares the available quote and unavailable/invalid cases against the same
Python inventory rules. It stops the server when complete. The first restore
needs internet; no model or API key is used.

Predict first: will a boolean guest count be treated as one guest? It is rejected.
JSON booleans are not numeric counts, even though some languages blur that boundary.

The [wire capture](../wire/dotnet.jsonl) is actual JSON-RPC traffic. TaskUpdater
submits work, emits a quote artifact and completes or rejects the task.
ASP.NET middleware protects the whole protocol endpoint. Discovery remains public.

This is a single-partner, in-memory lab. It does not implement multi-tenant task
ownership or production TLS. The Python main track covers owner isolation; do not
reuse this local deployment as a public multi-user service.

Source: [official preview release](https://github.com/a2aproject/a2a-dotnet/releases/tag/v1.0.0-preview4).
