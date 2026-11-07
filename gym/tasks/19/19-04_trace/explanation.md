# Why it works

Cap both delay and attempts; persist retry state if delivery must survive a restart.

A persistent task store survives process loss; an in-memory event queue does not coordinate multiple replicas. The current SDK offers a database event stream and versioned database store, which must be paired correctly. Proxies need streaming timeouts and buffering disabled. Webhook retry requires a durable outbox for crash recovery. Docker packages the process; it does not automatically provide trust or persistence.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
