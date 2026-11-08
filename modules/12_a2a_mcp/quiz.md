# Quiz

1. Who calls the kitchen MCP tool?
<details><summary>Answer</summary>Saffron calls it internally. The Concierge communicates with Saffron through A2A.</details>

2. What is lost by flattening a task into a tool string?
<details><summary>Answer</summary>Continuation, cancellation, ownership, status history and artifact structure unless explicitly mapped.</details>

3. Does an in-memory MCP transport use the real SDK?
<details><summary>Answer</summary>Yes. The course runs the actual server/client APIs without opening a network socket.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Choose a tool versus a remote agent: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>MCP connects a host to tools and resources; A2A connects independently operated agents. Inventory lookup belongs inside Saffron Table as a tool, while menu quoting can remain a remote task. A bridge must decide how to represent task IDs, interruption, streaming and authorization. Turning every task into a single tool return can lose progress and continuation.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
