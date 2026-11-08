# Quiz

1. Why isolate some framework dependencies?
<details><summary>Answer</summary>Their native A2A extras require incompatible legacy SDK versions; the course keeps the official v1 boundary in its core environment.</details>

2. Which layer owns lifecycle semantics?
<details><summary>Answer</summary>The shared A2A adapter. Frameworks execute internal workflows without redefining protocol states.</details>

3. Does an adapter test prove every framework-native client combination?
<details><summary>Answer</summary>No. It proves the documented adapter and runtime; the compatibility matrix states that scope explicitly.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Separate framework internals from the protocol: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A framework supplies internal agent execution; A2A supplies the external contract. A native adapter may lag the protocol, so inspect its dependency range and emitted card before using it. An official-SDK boundary can wrap a framework's public invocation API when its native adapter is incompatible. Test the combination, not just each package independently.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
