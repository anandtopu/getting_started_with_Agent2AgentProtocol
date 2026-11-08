# Quiz

1. Is a decoded JWT proof of authorization?
<details><summary>Answer</summary>No. Verify signature, algorithm, issuer, audience, expiry and required scope.</details>

2. Where are credentials obtained?
<details><summary>Answer</summary>Outside A2A messages through the configured identity mechanism; send them in the appropriate headers or TLS handshake.</details>

3. What protects partner-only pricing?
<details><summary>Answer</summary>Authenticated scope checks at the operation and extended-card boundary, not secrecy of the skill description.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Reject missing credentials: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Authentication proves identity; authorization decides what that identity may do. A card advertises schemes but does not issue credentials. Obtain API keys or OAuth tokens out of band. A JWT is signed claims, not proof until issuer, audience, signature and expiration are checked. OpenID Connect adds identity discovery to OAuth. TLS protects the connection; mutual TLS also verifies a client certificate.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
