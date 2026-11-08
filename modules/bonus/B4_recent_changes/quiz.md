# Quiz

1. Does SDK 1.3 imply protocol 1.3?
<details><summary>Answer</summary>No. This SDK implements the advertised protocol 1.0 contract while adding runtime features.</details>

2. How do you verify an upgrade?
<details><summary>Answer</summary>Review release/migration notes, update the lock intentionally, and rerun contracts, golden, native and recovery checks.</details>

3. Why preserve raw upstream failures?
<details><summary>Answer</summary>They distinguish implementation regressions from reviewed external contradictions and prevent false compatibility claims.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Separate SDK and protocol releases: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Package versions and protocol versions are separate. SDK 1.3 can implement protocol 1.0 while adding runtime features such as shared event delivery. Re-run compatibility tests after a dependency update and retain the lockfile. Prefer demonstrated behavior over copying examples from an overview that may contain stale field names.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
