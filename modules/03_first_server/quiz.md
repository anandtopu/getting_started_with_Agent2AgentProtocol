# Quiz

1. When should the executor enqueue a Task?
<details><summary>Answer</summary>Once for newly created work. A resumed task receives updates rather than a second paused snapshot.</details>

2. Who implements routing?
<details><summary>Answer</summary>The SDK route factories and request handler; the executor performs the business workflow.</details>

3. Can an executor mix queue events and yielded events?
<details><summary>Answer</summary>No. Choose one SDK streaming pattern; mixing them can duplicate or lose output.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Compose SDK routes: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>The executor performs business work. The SDK handles routing, serialization, task storage and subscribers. An async function cooperatively yields while waiting rather than blocking other work. A new task starts with a Task event. Thereafter it produces status and artifact updates. A one-message response is a separate pattern and cannot be mixed with task events. The current SDK owns snapshots when resuming stored tasks.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
