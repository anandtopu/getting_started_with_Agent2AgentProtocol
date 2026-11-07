# Native Go venue agent

Install Go 1.26+, then run from the repository root:

~~~console
uv run python scripts/check_go_interop.py
~~~

The checker builds the official SDK v2.8.0 implementation, starts it on
127.0.0.1:8400 with a fresh bearer token, discovers it, verifies unauthenticated
calls fail and compares the returned quote with the Python inventory calculation.
It stops its own process afterward. Dependency installation initially needs internet.

The executor reads the committed synthetic venue dataset, accepts guests and date,
and returns an A2A task with a structured quote artifact. Integer cents avoid
floating-point money calculations. No booking or purchase occurs. The local
single-partner example uses memory storage; public hosting needs TLS and
separate identities.

Source: [official Go SDK release](https://github.com/a2aproject/a2a-go/releases/tag/v2.8.0).
