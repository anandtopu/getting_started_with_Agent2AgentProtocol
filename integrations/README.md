# Seven frameworks, one A2A boundary

The main course uses official A2A Python SDK 1.3.0. LangGraph runs directly in that
environment. The six workers below run in separate locked environments; their
framework-specific models and workflows never replace the public A2A 1.x handler.

This matters when a framework's native A2A extra still requires SDK 0.3. Installing
that extra into the course would downgrade its protocol implementation. We instead
keep the framework's business workflow opaque behind a current, verified adapter.

| Framework | Pinned runtime | Executed API | A2A boundary |
|---|---|---|---|
| Google ADK | 2.14.0 | BaseAgent, InMemoryRunner, session events | Official SDK 1.3.0 adapter |
| LangGraph | 1.2.20 | StateGraph, two nodes, ainvoke, private MCP tool | Official SDK 1.3.0 adapter |
| Strands Agents | 1.64.0 | Agent.invoke_async with a scripted Model event stream | Official SDK 1.3.0 adapter |
| Pydantic AI | slim 2.66.0 | Agent.run with FunctionModel | Official SDK 1.3.0 adapter |
| CrewAI | 1.15.37 | Agent, Task, Crew.kickoff_async with BaseLLM | Official SDK 1.3.0 adapter |
| Microsoft Agent Framework | core 1.25.0 | executor, WorkflowBuilder, yield_output | Official SDK 1.3.0 adapter |
| BeeAI | 0.1.86 | Workflow, typed state and an async step | Official SDK 1.3.0 adapter |

## Install and run

Initial installation needs internet and more disk space than the core course.
It does not need a model API key.

~~~console
uv run python scripts/setup_frameworks.py
uv run python scripts/check_frameworks.py
uv run python scripts/network.py up --module 11 --frameworks
~~~

The live network maps Granite to ADK, Saffron to Strands, Brightline to Pydantic AI,
Northstar to CrewAI and Inkwell to BeeAI. Inkwell still exposes only gRPC operations.
The Concierge verifies signed cards and delegates with separate vendor tokens.
Microsoft's workflow is verified through the same adapter independently.

The checker starts a real in-process A2A server for each worker, pauses Saffron for
dietary counts, resumes the same task and asserts the final quote against inventory.
The worker itself uses the real framework runtime with external sockets disabled.
ADK, Microsoft and BeeAI execute deterministic framework workflows; Strands,
Pydantic AI and CrewAI execute scripted model providers. These checks establish
framework and protocol interoperability, not live-model quality.

Use --framework adk (or another table key: strands, pydantic, crewai, microsoft,
beeai) with either setup_frameworks.py or check_frameworks.py to target one runtime.
Use --capture with the checker to refresh the module's actual traffic.

## Under the hood

~~~mermaid
sequenceDiagram
    participant C as Concierge
    participant S as Official A2A v1 server
    participant W as Isolated framework worker
    C->>S: Authenticated A2A message
    S->>S: Preserve task and context IDs
    S->>W: Minimal JSON brief over stdin
    W->>W: Real framework execution, scripted model if needed
    W-->>S: Structured quote over stdout
    S-->>C: Artifact and terminal status
~~~

Credentials and signing keys are removed from the worker environment. The parent
bounds execution to 90 seconds and kills the owned worker on cancellation. A
production process pool could avoid per-request interpreter startup, but must keep
the same credential boundary, task ownership and resource limits.

The adapter is [agents/framework_vendor.py](../agents/framework_vendor.py); the
framework APIs are visible together in [worker.py](worker.py). Every project
contains a pyproject.toml and uv.lock. No incompatible native A2A extra is installed.

This is not an exhaustive framework-native client/server cross-product. It verifies
each runtime behind the shared v1 boundary, plus a live heterogeneous vendor network.
