# Why it works

Introduce the task before updates and explicitly reach a final state.

The executor performs business work. The SDK handles routing, serialization, task storage and subscribers. An async function cooperatively yields while waiting rather than blocking other work. A new task starts with a Task event. Thereafter it produces status and artifact updates. A one-message response is a separate pattern and cannot be mixed with task events. The current SDK owns snapshots when resuming stored tasks.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
