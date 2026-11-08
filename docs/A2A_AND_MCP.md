# A2A and MCP

| Question | A2A | MCP |
|---|---|---|
| Typical boundary | Independently operated agents | A host and its tools/resources |
| Example | Concierge asks Saffron for a menu quote | Saffron reads kitchen inventory |
| Work representation | Messages, tasks, artifacts and progress | Tool/resource interactions |
| Internal implementation exposed? | Not required | Tool interfaces are explicitly described |
| Trust decision | Which remote agent may receive which brief? | Which host may invoke which tool? |

~~~mermaid
flowchart LR
    C["Maplewood Concierge"] -->|A2A| S["Saffron Table"]
    S -->|MCP| I["Kitchen inventory"]
    C -->|A2A| V["Granite Hall"]
~~~

Use a tool when the operation is a bounded capability inside your application.
Use a remote agent when independent ownership, execution or coordination matters.
A bridge must deliberately map continuation, cancellation, streaming, credentials
and errors. Returning a long-running task as one string loses important information.

The [kitchen server](../agents/kitchen.py) uses the actual MCP server and client SDK,
with its in-memory transport for offline grading and stdio for a standalone process.
The [LangGraph executor](../agents/langgraph_vendor.py) invokes that kitchen privately
and reports only validated A2A artifacts. Run `uv run python -m agents.kitchen` for
the stdio server, or module 12's examples for the complete in-process integration.
