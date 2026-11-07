# Tier 2: desk reference

**Putting an LLM behind a server** — A language model predicts output from context; it is not the protocol and should not calculate binding prices. A tool call asks application code to run a named function with validated arguments. The course first scripts model decisions, making failures repeatable and free. Provider configuration lives in one helper. Every tool loop has a step limit and every business action has validation.

**The orchestrator** — The Concierge is an A2A client of vendors and can also be an A2A server for callers. It delegates independent quotes concurrently and returns partial results when one vendor needs input. Remote context IDs are owned by each vendor; retain a mapping rather than assuming one global context works everywhere. Give each vendor its own service credential and only the brief fields it needs.

**Framework integrations** — A framework supplies internal agent execution; A2A supplies the external contract. A native adapter may lag the protocol, so inspect its dependency range and emitted card before using it. An official-SDK boundary can wrap a framework's public invocation API when its native adapter is incompatible. Test the combination, not just each package independently.

**A2A and MCP together** — MCP connects a host to tools and resources; A2A connects independently operated agents. Inventory lookup belongs inside Saffron Table as a tool, while menu quoting can remain a remote task. A bridge must decide how to represent task IDs, interruption, streaming and authorization. Turning every task into a single tool return can lose progress and continuation.

Practice: uv run gym list --module NN; uv run gym next; uv run gym drill.
