# Quiz

1. Can signed skill text override the user's requested vendor scope?
<details><summary>Answer</summary>No. Signatures establish origin, not authority to expand the task.</details>

2. Why block private file addresses?
<details><summary>Answer</summary>They can target internal services or cloud metadata endpoints.</details>

3. Why is a redirect a separate trust decision?
<details><summary>Answer</summary>It changes the destination after the initial URL was approved.</details>

4. What stops a poisoned quote from approving payment?
<details><summary>Answer</summary>A strict output contract and a separate human approval gate.</details>

5. What prevents delegation from leaking unrelated fields?
<details><summary>Answer</summary>A per-vendor payload allow-list enforced in code.</details>

6. What makes a callback replay distinguishable?
<details><summary>Answer</summary>An authenticated timestamp and delivery ID plus replay or durable inbox state.</details>
