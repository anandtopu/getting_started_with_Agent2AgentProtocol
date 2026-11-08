# Quiz

1. When is one process preferable to A2A services?
<details><summary>Answer</summary>When work shares ownership and lifecycle and independent deployment adds little value.</details>

2. Does canceling an A2A task undo a completed hold?
<details><summary>Answer</summary>No. A release skill performs the compensating business action.</details>

3. Why use a stable hold request ID?
<details><summary>Answer</summary>Retries can reconcile the same business operation instead of creating duplicate holds.</details>

4. What if a hold committed but its confirmation is malformed?
<details><summary>Answer</summary>Treat the outcome as uncertain and reconcile by its idempotency key.</details>

5. What if cleanup cannot be confirmed?
<details><summary>Answer</summary>Report manual follow-up explicitly rather than claiming compensation succeeded.</details>

6. What belongs in an architecture decision record?
<details><summary>Answer</summary>Context, alternatives, chosen boundaries, measurable tradeoffs and failure policy.</details>
