# Why the repair works

Fetch approved public artwork, but block private and metadata-service destinations before an HTTP call.

The solution is checked at the actual protocol boundary. A passing happy path is insufficient: the grader also asserts task identity, trust, ownership, or transport effects relevant to this task. Read gym/protocol_checks.py after solving to inspect the acceptance checks.

Common wrong answer: changing the expected result instead of the defective boundary. Only workspace files are editable; the trusted grader remains outside the attempt.
