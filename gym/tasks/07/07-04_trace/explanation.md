# Why it works

Append only to an existing artifact with the same ID.

Server-Sent Events (SSE) keep an HTTP response open and separate events with blank lines. A chunk updates one artifact by ID: append means add to existing content, and lastChunk ends that artifact. It does not finish the task. A webhook reverses the connection: the vendor calls your receiver later. Authenticate deliveries and tolerate retries. Reconnecting with SubscribeToTask does not promise replay of every missed event.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
