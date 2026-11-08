# Quiz

1. Does lastChunk finish the task?
<details><summary>Answer</summary>No. It completes one artifact. Task status determines task completion.</details>

2. Does disconnecting SSE cancel the work?
<details><summary>Answer</summary>No. Reconnect with SubscribeToTask or inspect GetTask; cancellation is explicit.</details>

3. Why deduplicate an authenticated callback?
<details><summary>Answer</summary>The receiver may commit before its acknowledgement is lost, causing a legitimate retry.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Read SSE frames: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Server-Sent Events (SSE) keep an HTTP response open and separate events with blank lines. A chunk updates one artifact by ID: append means add to existing content, and lastChunk ends that artifact. It does not finish the task. A webhook reverses the connection: the vendor calls your receiver later. Authenticate deliveries and tolerate retries. Reconnecting with SubscribeToTask does not promise replay of every missed event.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
