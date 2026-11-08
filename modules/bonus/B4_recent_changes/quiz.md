# Quiz

1. Does Python SDK 1.3 mean protocol 1.3?
<details><summary>Answer</summary>No. This SDK implements the targeted 1.0 protocol family.</details>

2. Why keep pagination tokens opaque?
<details><summary>Answer</summary>They are server-owned continuation data, not offsets to invent or edit.</details>

3. What changes when interrupted tasks are parked?
<details><summary>Answer</summary>Runtime resources can be released while durable task state remains available.</details>

4. What must a shared-store upgrade preserve?
<details><summary>Answer</summary>Ownership, revision safety, event ordering and recovery behavior.</details>

5. Is a release-note claim enough to mark a feature verified?
<details><summary>Answer</summary>No. Run a focused example or regression against the pinned version.</details>

6. Where should confirmed swaps and limitations be recorded?
<details><summary>Answer</summary>In VERIFICATION_NOTES and the validation report.</details>
