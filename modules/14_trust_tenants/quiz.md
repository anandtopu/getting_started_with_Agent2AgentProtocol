# Quiz

1. Which card field is excluded from the signed payload?
<details><summary>Answer</summary>signatures itself.</details>

2. Why canonicalize JSON before signing?
<details><summary>Answer</summary>Equivalent JSON formatting and key order should produce the same signing bytes.</details>

3. Can a key URL in an untrusted card establish trust?
<details><summary>Answer</summary>No. Use separately configured keys or an operator-pinned HTTPS source.</details>

4. Why overlap keys during rotation?
<details><summary>Answer</summary>Previously cached cards must remain verifiable for their allowed lifetime.</details>

5. Does a signed card authorize reading a task?
<details><summary>Answer</summary>No. Task ownership comes from authenticated request identity.</details>

6. What should a malformed signature header do?
<details><summary>Answer</summary>Fail validation cleanly without accepting the card or crashing orchestration.</details>
