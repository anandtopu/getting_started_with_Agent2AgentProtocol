# Quiz

1. Does an offline exercise need Ollama?
<details><summary>Answer</summary>No. The deterministic agents and scripted models require neither a provider nor API keys.</details>

2. What changes when you switch vendors?
<details><summary>Answer</summary>The skill and endpoint change; messages, tasks and artifacts retain the protocol contract.</details>

3. What does HTTP carry here?
<details><summary>Answer</summary>A request and response containing JSON-RPC, HTTP+JSON or an SSE stream; gRPC uses its own HTTP/2 framing.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Discover a vendor: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A2A gives independently operated agents a shared contract. A vendor can change its internal code without changing how Maplewood discovers its skills or requests a quote. HTTP is a request and response exchange; JSON is the text format used for structured values. Start with a ready-made deterministic agent so that networking and model behavior do not become tangled.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
