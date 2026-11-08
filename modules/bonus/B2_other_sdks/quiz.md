# Quiz

1. Is every official SDK stable?
<details><summary>Answer</summary>No. The verified .NET SDK is 1.0.0-preview4; official status and stable release status differ.</details>

2. Which Java boundary needs an auth filter?
<details><summary>Answer</summary>The SDK Vert.x router. A Jakarta REST filter alone does not protect that router.</details>

3. What does the native test matrix cover?
<details><summary>Answer</summary>Authentication, quote and invalid-input behavior through Python clients on Linux, Windows and macOS.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Inspect language compatibility: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Official SDK status does not guarantee that every language release supports the same protocol revision. Check Go, Java and .NET release notes and minimum runtimes before selecting versions. Run the same request and compare semantics, allowing generated IDs and timestamps to differ.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
