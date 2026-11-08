# Quiz

1. Can an authentic vendor inject malicious instructions?
<details><summary>Answer</summary>Yes. Authentication identifies a sender; its descriptions and artifacts remain untrusted data.</details>

2. Why disable redirects when fetching files?
<details><summary>Answer</summary>An approved initial URL could redirect to an internal or otherwise forbidden destination.</details>

3. Why use separate vendor credentials?
<details><summary>Answer</summary>Least privilege limits audience and scope and prevents the Concierge from becoming a confused deputy with the user token.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Reject unsafe destinations: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Treat cards, messages and artifacts as untrusted inputs. Prompt injection attempts to turn those inputs into higher-priority instructions. Allow-list destinations, validate outputs, keep tokens scoped, and require human approval before spending. Private-address filtering alone does not prevent DNS rebinding; use a controlled egress path or inline files. Limit bytes, duration, concurrency and tool steps.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
