# Quiz

1. What does execute receive?
<details><summary>Answer</summary>The request context and event queue used to publish task events.</details>

2. Who stores the task snapshot?
<details><summary>Answer</summary>The SDK handler and its configured task store.</details>

3. Can an executor mix a direct Message with task updates?
<details><summary>Answer</summary>No. Choose one of the mutually exclusive response patterns.</details>

4. What must happen before execute returns?
<details><summary>Answer</summary>Tracked work must reach a terminal or paused state.</details>

5. Should a resumed task emit its original Task again?
<details><summary>Answer</summary>No. Continue with updates; the SDK owns the resumed snapshot.</details>

6. Why first build a server without the SDK?
<details><summary>Answer</summary>To see routing and envelope mechanics before the SDK manages the full protocol.</details>
