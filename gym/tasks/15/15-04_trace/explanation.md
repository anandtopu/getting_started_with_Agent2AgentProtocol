# Why it works

This IP check is one layer; production fetches also need allow-lists, no redirects and DNS rebinding protection.

Treat cards, messages and artifacts as untrusted inputs. Prompt injection attempts to turn those inputs into higher-priority instructions. Allow-list destinations, validate outputs, keep tokens scoped, and require human approval before spending. Private-address filtering alone does not prevent DNS rebinding; use a controlled egress path or inline files. Limit bytes, duration, concurrency and tool steps.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
