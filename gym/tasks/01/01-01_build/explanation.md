# Why it works

The method parameters contain a message object, not its individual fields.

A message is a communication; a task is tracked work; an artifact is its deliverable. A context groups related interactions, like a project folder. JSON-RPC adds a method name, parameters and request ID to a JSON envelope. Its request ID correlates the response and is different from messageId and task ID. A server may return a direct Message or a Task.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
