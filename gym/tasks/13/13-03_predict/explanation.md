# Why it works

Authentication alone does not grant partner pricing.

Authentication proves identity; authorization decides what that identity may do. A card advertises schemes but does not issue credentials. Obtain API keys or OAuth tokens out of band. A JWT is signed claims, not proof until issuer, audience, signature and expiration are checked. OpenID Connect adds identity discovery to OAuth. TLS protects the connection; mutual TLS also verifies a client certificate.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
