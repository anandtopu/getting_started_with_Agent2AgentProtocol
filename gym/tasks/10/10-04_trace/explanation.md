# Why it works

Pass only the business fields required by the selected vendor.

The Concierge is an A2A client of vendors and can also be an A2A server for callers. It delegates independent quotes concurrently and returns partial results when one vendor needs input. Remote context IDs are owned by each vendor; retain a mapping rather than assuming one global context works everywhere. Give each vendor its own service credential and only the brief fields it needs.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
