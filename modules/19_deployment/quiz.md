# Quiz

1. Does a SQL task store alone make SSE work across replicas?
<details><summary>Answer</summary>No. Replicas also need a shared event stream or journal.</details>

2. Why commit the outbox with the task snapshot?
<details><summary>Answer</summary>A crash must not leave committed work without its notification record.</details>

3. What prevents stale task writers from overwriting newer work?
<details><summary>Answer</summary>A compare-and-swap revision check in the database transaction.</details>

4. Why fence dispatcher leases?
<details><summary>Answer</summary>An expired worker must not acknowledge another worker's newer claim.</details>

5. Why disable proxy buffering for SSE?
<details><summary>Answer</summary>Otherwise progress can arrive only after the response finishes.</details>

6. What operational work remains beyond a green Compose test?
<details><summary>Answer</summary>Certificate renewal, backups, retention, monitoring and capacity planning.</details>
