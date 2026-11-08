# Quiz

1. Do golden tests establish conformance?
<details><summary>Answer</summary>No. They evaluate business outcomes; protocol contract tests and the official TCK exercise different properties.</details>

2. What does the green TCK regression job mean?
<details><summary>Answer</summary>No unexpected deviation from the documented baseline; four exact upstream contradictions remain raw failures.</details>

3. What should a reconnect chaos test prove?
<details><summary>Answer</summary>A disconnected subscriber can reconcile the task and continue through a second handler without losing a committed terminal event.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Run offline contracts: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>An offline contract test should observe actual routing and serialized responses. Conformance checks protocol behavior; evaluation checks business outcomes. The official TCK expects a reachable server and is a separate integration job. Course tests do not certify official compliance. Record and redact traffic, inject failures and assert the sequence that a client can observe.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
