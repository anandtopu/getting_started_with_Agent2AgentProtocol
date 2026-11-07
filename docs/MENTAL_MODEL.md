# One request through the network

~~~mermaid
sequenceDiagram
    participant U as Event planner
    participant C as Concierge
    participant V as Vendor
    participant R as Callback receiver
    C->>V: GET well-known Agent Card
    V-->>C: Skills, interfaces, security
    U->>C: Event brief
    C->>V: SendMessage + credential header
    V-->>C: Task with work-order ID
    alt Missing information
        V-->>C: INPUT_REQUIRED
        C-->>U: Dietary-count question
        U->>C: Counts
        C->>V: New message with existing task/context IDs
    end
    V-->>C: Quote artifact + COMPLETED
    opt Push configured
        V->>R: Authenticated StreamResponse notification
    end
    C-->>U: Quotes requiring approval
~~~

The Agent Card is a business card. A task is a work order. An artifact is a
deliverable. A context is a project folder owned by the agent that created it.

JSON-RPC wraps an operation name in a JSON envelope. HTTP+JSON uses distinct
HTTP routes. gRPC calls generated methods with protobuf messages. Those are
transport choices; they do not change who owns the task.

For streaming, JSON-based bindings use SSE and gRPC uses server streaming.
Polling asks for a snapshot. Push delivery makes the server a client of a
separately authenticated receiver. None of these makes distributed execution
exactly once or guarantees that a disconnected client saw every event.
