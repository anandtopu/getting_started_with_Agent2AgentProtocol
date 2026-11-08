# Quiz

1. When may a streamed tool call execute?
<details><summary>Answer</summary>Only after a complete finish event, allowed tool name, byte/deadline checks and argument schema validation.</details>

2. Should private reasoning become an A2A artifact?
<details><summary>Answer</summary>No. Emit safe progress and the validated deliverable, not internal reasoning or partial tool arguments.</details>

3. How does missing dietary input become protocol state?
<details><summary>Answer</summary>The workflow maps missing required inputs to TASK_STATE_INPUT_REQUIRED and waits for continuation.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Replace model output with a script: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A language model predicts output from context; it is not the protocol and should not calculate binding prices. A tool call asks application code to run a named function with validated arguments. The course first scripts model decisions, making failures repeatable and free. Provider configuration lives in one helper. Every tool loop has a step limit and every business action has validation.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
