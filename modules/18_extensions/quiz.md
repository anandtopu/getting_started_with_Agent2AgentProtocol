# Quiz

1. Does declaring an extension activate it on every request?
<details><summary>Answer</summary>No. Activation is request-time negotiation.</details>

2. What header carries requested extensions?
<details><summary>Answer</summary>A2A-Extensions.</details>

3. What if a required extension is missing?
<details><summary>Answer</summary>Reject the incompatible request rather than silently ignoring the requirement.</details>

4. May the quote extension invent a new core TaskState?
<details><summary>Answer</summary>No. It adds agreed semantics without redefining core states.</details>

5. Are agent product and protocol versions identical?
<details><summary>Answer</summary>No. The interface carries its protocol version separately.</details>

6. How should a breaking skill change be introduced?
<details><summary>Answer</summary>Version its contract and provide an explicit migration path.</details>
