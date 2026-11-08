# Quiz

1. What identifies chunks of the same artifact?
<details><summary>Answer</summary>The artifact ID within its task.</details>

2. What does append=true mean?
<details><summary>Answer</summary>Append the new Parts to the existing artifact instead of replacing it.</details>

3. Does lastChunk mean the task completed?
<details><summary>Answer</summary>No. It finishes that artifact; task completion is a separate status event.</details>

4. What operation follows a dropped stream?
<details><summary>Answer</summary>SubscribeToTask for the existing active task when supported.</details>

5. Why authenticate a webhook before deduplicating it?
<details><summary>Answer</summary>An attacker must not poison the inbox with an unauthenticated delivery ID.</details>

6. Is exactly-once delivery promised?
<details><summary>Answer</summary>No. Durable receivers deduplicate at-least-once delivery attempts.</details>
