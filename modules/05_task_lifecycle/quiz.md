# Quiz

1. Which states are terminal?
<details><summary>Answer</summary>Completed, failed, canceled and rejected. Input-required and auth-required are pauses.</details>

2. Does CancelTask undo a completed booking?
<details><summary>Answer</summary>No. Cancellation changes task execution; a compensating business operation releases a hold.</details>

3. Are page tokens offsets?
<details><summary>Answer</summary>No. Treat them as opaque and pass nextPageToken back to the server.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Resume a paused catering task: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Submitted and working are active states. Input-required and auth-required interrupt work without ending the task. Completed, failed, canceled and rejected are terminal: create a new task for new work after these states. Keep task and context IDs when answering a request for missing input. The wire uses uppercase protobuf enum names. TASK_STATE_UNSPECIFIED is a sentinel, not a useful success state.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
