# Quiz

1. What joins spans across agents?
<details><summary>Answer</summary>W3C trace context in HTTP headers or gRPC metadata, with matching trace IDs and correct parent spans.</details>

2. Why avoid task IDs as metric labels?
<details><summary>Answer</summary>Their unbounded cardinality can exhaust a metrics backend; use bounded vendor labels and span attributes for IDs.</details>

3. What does a golden scenario compare?
<details><summary>Answer</summary>Delegated vendors, exact state sequences, artifact IDs/chunks and structured quote values.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Read related spans: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A trace groups spans for one distributed request; a span records one operation. Propagate W3C trace context through transports and correlate task IDs without making them authorization credentials. Course attribute names are explicitly application conventions. Golden scenarios check delegations, states and artifacts, not whether prose sounds convincing. Never log tokens or entire sensitive briefs.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
