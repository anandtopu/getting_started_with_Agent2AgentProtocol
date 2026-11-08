# Quiz

1. Is an artifact a task?
<details><summary>Answer</summary>No. A task tracks work; an artifact is a deliverable produced by that work.</details>

2. Can SendMessage return no task?
<details><summary>Answer</summary>Yes. A direct Message is a valid alternative to a tracked Task.</details>

3. Which ID correlates a JSON-RPC response?
<details><summary>Answer</summary>The JSON-RPC id, not messageId, task id or contextId.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Read a JSON-RPC envelope: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A message is a communication; a task is tracked work; an artifact is its deliverable. A context groups related interactions, like a project folder. JSON-RPC adds a method name, parameters and request ID to a JSON envelope. Its request ID correlates the response and is different from messageId and task ID. A server may return a direct Message or a Task.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
