# Quiz

1. Which states are paused?
<details><summary>Answer</summary>INPUT_REQUIRED and AUTH_REQUIRED.</details>

2. Which states are terminal?
<details><summary>Answer</summary>COMPLETED, FAILED, CANCELED and REJECTED.</details>

3. Which IDs continue a paused conversation?
<details><summary>Answer</summary>The remote task ID and its context ID.</details>

4. Does contextId alone resume a task?
<details><summary>Answer</summary>No. Supply taskId for the particular interrupted work.</details>

5. Can CancelTask undo a completed hotel hold?
<details><summary>Answer</summary>No. Use an explicit compensating release skill.</details>

6. Do repeated message IDs guarantee exactly-once work?
<details><summary>Answer</summary>No. Application idempotency must protect business effects.</details>
