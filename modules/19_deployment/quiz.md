# Quiz

1. What must commit atomically?
<details><summary>Answer</summary>Task snapshot, revision, durable event and callback outbox entry.</details>

2. Why does a dispatcher need a lease token?
<details><summary>Answer</summary>It fences acknowledgements from an expired worker after another worker claims the delivery.</details>

3. Does a database task store alone recover streams?
<details><summary>Answer</summary>No. Replicas also need a shared event journal and consistent snapshot/cursor behavior.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Persist and reload a task: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A persistent task store survives process loss; an in-memory event queue does not coordinate multiple replicas. The current SDK offers a database event stream and versioned database store, which must be paired correctly. Proxies need streaming timeouts and buffering disabled. Webhook retry requires a durable outbox for crash recovery. Docker packages the process; it does not automatically provide trust or persistence.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
