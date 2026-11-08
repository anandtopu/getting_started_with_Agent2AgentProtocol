# Quiz

1. When is an in-process function preferable?
<details><summary>Answer</summary>When ownership and deployment are shared and lower latency/simpler failure handling matter more than an independent boundary.</details>

2. What is compensation?
<details><summary>Answer</summary>A new business action such as releasing a hold; it is not a distributed database rollback.</details>

3. What if cleanup cannot be confirmed?
<details><summary>Answer</summary>Report manual follow-up and retain a stable business request ID for reconciliation; do not claim success.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Choose useful agent boundaries: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Choose agent boundaries around ownership, independent deployment and durable responsibilities. An in-process function call is often simpler for tightly coupled work. Distributed requests can partially succeed. Compensating actions are new business operations, such as releasing a hold; they are not database rollback across organizations. Write an architecture decision record that states alternatives, failure handling and measurable tradeoffs.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
