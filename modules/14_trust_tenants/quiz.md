# Quiz

1. What does JCS canonicalization solve?
<details><summary>Answer</summary>Equivalent JSON key ordering produces the same signing input; the signatures field itself is excluded.</details>

2. Can a card choose its own trusted JWKS URL?
<details><summary>Answer</summary>No. Trust comes from operator-pinned keys or a configured HTTPS vendor endpoint.</details>

3. Why share a key ring across replicas?
<details><summary>Answer</summary>A card signed by one replica must verify against JWKS served by another, including during rotation and restart.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Sign canonical card bytes: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A signature detects changes to a card and binds it to a key you already trust. Canonical JSON makes equivalent objects produce the same signed bytes. JWS specifies how headers and payload are signed. A JWKS is a set of public keys; a key URL advertised by an attacker is not automatically trusted. Tenant routing is separate from authenticated ownership.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
