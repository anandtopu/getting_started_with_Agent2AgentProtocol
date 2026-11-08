# Quiz

1. When is retrying a quote safe?
<details><summary>Answer</summary>A read-only quote can be retried within a deadline; a business effect requires a documented durable idempotency key.</details>

2. Does contextId resume a task?
<details><summary>Answer</summary>No. taskId identifies the paused task; contextId groups related work.</details>

3. What does returnImmediately mean?
<details><summary>Answer</summary>Acknowledge accepted work without waiting for completion; poll or subscribe to the task afterward.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Create an SDK client: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>The client reads the card and selects an interface it understands. It sends A2A-Version: 1.0 and authenticates in headers. A timeout means the caller did not see a result; it does not prove that work was not performed. Retrying a purchase blindly can duplicate spending. Message IDs identify messages, but the protocol does not grant universal exactly-once execution.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
