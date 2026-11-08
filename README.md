# Getting started with the Agent2Agent Protocol

Learn A2A by building **Maplewood Events** and its independent vendor network.
You need basic Python, a terminal and Git. You do not need an LLM, API keys or a
cloud account for the examples and graded exercises.

**Target:** A2A specification **1.0.1**, official Python SDK **1.3.0**.
The course includes 21 core modules, four bonus modules, 83 runnable examples,
265 graded exercises and five capstones. Build deterministic agents first, then add
native model tool streams, framework interoperability, heterogeneous authentication,
and a durable encrypted deployment. See the [validation report](docs/VALIDATION_REPORT.md)
for executed checks and the [feature companion](docs/FEATURE_DEEP_DIVES.md) for deeper explanations.

A2A is an open protocol for independently operated agents to exchange work.
An **Agent Card** describes a vendor's skills and interfaces. A **message**
communicates a request. A **task** tracks work, and an **artifact** contains a
deliverable. JSON-RPC, HTTP+JSON and gRPC carry the same abstract operations.
The normative definition is [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).
The [Linux Foundation project](https://github.com/a2aproject/A2A) maintains the standard.

A2A connects agents; MCP connects a host to its tools and resources. Neither
requires exposing an agent's internal reasoning or memory.

## What you build

| Agent | Responsibility |
|---|---|
| Granite Hall Venues | Room availability and venue quotes |
| Saffron Table Catering | Dietary clarification and menu quotes |
| Brightline AV | Streamed equipment plans |
| Northstar Travel Desk | Public and authorized partner hotel prices |
| Inkwell Print Co. | Badge estimates and protobuf interoperability |
| Maplewood Concierge | Bounded delegation, validated quotes and approval gates |

All names, events and inventory in the course data are fictional.

## Five-minute quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git.
Python 3.11–3.13 is supported. Node is optional until the TypeScript bonus.
These commands work in **Windows PowerShell, macOS and Linux**:

~~~console
git clone https://github.com/anandtopu/getting_started_with_Agent2AgentProtocol.git
cd getting_started_with_Agent2AgentProtocol
uv sync
uv run python scripts/network.py up --module 00
~~~

Keep that terminal open. In a second terminal in the same folder:

~~~console
uv run python scripts/talk.py venues
uv run gym start 00-01
~~~

Edit the function in **workspace/00-01/solution.py** so it returns the URL
http://127.0.0.1 followed by a colon and the port supplied in the payload.
Then:

~~~console
uv run gym check 00-01
uv run gym next
uv run python scripts/network.py down
~~~

After the first dependency download, the gym and in-process examples run offline:

~~~console
uv run --offline python modules/05_task_lifecycle/examples/02_resume.py
uv run --offline pytest
~~~

The first network demos intentionally omit authentication and bind only to loopback.
Module 04 onward uses generated per-vendor credentials stored in ignored workspace
files. Real deployments need TLS and managed credentials.

## Choose your path

- Work through [the learning path](LEARNING_PATH.md) in order.
- Drill with the [Practice Gym](docs/GYM_TASKS.md): list, start, check, hint,
  solution, reset, progress, next and drill.
- Start a [capstone](capstones/README.md) and use modules as references.

~~~mermaid
flowchart LR
    A["00–08: Protocol foundations"] --> B["09–12: Models and orchestration"]
    B --> C["13–15: Trust and security"]
    C --> D["16–20: Testing and production"]
    D --> E["Bonuses and capstones"]
    G["Predict → Run → Explain → Practice"] --- A
    G --- B
    G --- C
    G --- D
~~~

| Tier | Reading and labs | Suggested additional practice |
|---|---:|---:|
| 1: Foundations | 12 hours | 6–10 hours |
| 2: Intelligent agents | 10 hours | 5–8 hours |
| 3: Security | 10 hours | 5–8 hours |
| 4: Production and design | 12 hours | 6–10 hours |
| Bonuses and capstones | Variable | 10–30 hours |

## Watch the network

~~~console
uv run python scripts/network.py up --module 08
uv run streamlit run control_room/app.py
~~~

The Control Room discovers cards, sends briefs and displays streamed events. Start
`uv run python scripts/webhook_lab.py` in another terminal to watch live signed
callbacks in its durable inbox panel.
For the current standalone A2A Inspector, use
[the official installation instructions](https://github.com/a2aproject/a2a-inspector).

## Validate the repository

~~~console
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/validate_gym.py
uv run python scripts/run_all_examples.py --notebooks
uv run python scripts/check_links.py
~~~

The offline gRPC harness exercises protobuf serialization and the real SDK
servicer without ports. Network gRPC and the official TCK are separate integration
checks. Design exercises have a human rubric; automated checks assess structure.

## FAQ

**Do I need an LLM?** No. Later examples use scripted model decisions. Optional
live models use .env.example and common/llm.py.

**Does initial installation work without internet?** No. Initial installation needs
package access. Later runs use the lockfile and cached packages offline.

**Can I deploy the final network?** Yes. Follow the [hardened deployment](deploy/HARDENED_NETWORK.md).
Operate certificates, backups and retention for your environment; passing course tests
is not an external production or protocol certification.

**Can I use a different model?** Yes. Configure the provider and model in .env.
Never commit credentials.

**Why did a task pass without a good design?** Design checks validate document
structure. A human must apply the rubric before claiming proficiency.

**Where are the exact messages?** Each module has captured exchanges under wire/.
Generated IDs and timestamps vary between runs.

Contributions: [CONTRIBUTING.md](CONTRIBUTING.md).
License: [MIT](LICENSE).

See [integration labs](docs/INTEGRATION_LABS.md), [all operations on the wire](docs/OPERATIONS_ON_THE_WIRE.md), and [the validation report](docs/VALIDATION_REPORT.md) for executed checks and external limitations.
