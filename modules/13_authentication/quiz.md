# Quiz

1. Does an authenticated caller automatically get partner pricing?
<details><summary>Answer</summary>No. The partner skill requires its own authorization scope.</details>

2. Where should bearer credentials travel?
<details><summary>Answer</summary>In the Authorization header, not message Parts.</details>

3. What does a wrong JWT audience mean?
<details><summary>Answer</summary>The token was issued for another service and must be rejected.</details>

4. How does mutual TLS identify a client?
<details><summary>Answer</summary>The TLS handshake verifies a client certificate under the configured trust policy.</details>

5. When is auth-required useful?
<details><summary>Answer</summary>When valid tracked work needs additional authorization obtained outside the conversation.</details>

6. Can a public Agent Card contain service secrets?
<details><summary>Answer</summary>No. It advertises mechanisms and requirements, not reusable credentials.</details>
