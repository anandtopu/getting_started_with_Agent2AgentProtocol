# Why it works

Input-required and auth-required are resumable; terminal states are not.

Submitted and working are active states. Input-required and auth-required interrupt work without ending the task. Completed, failed, canceled and rejected are terminal: create a new task for new work after these states. Keep task and context IDs when answering a request for missing input. The wire uses uppercase protobuf enum names. TASK_STATE_UNSPECIFIED is a sentinel, not a useful success state.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
