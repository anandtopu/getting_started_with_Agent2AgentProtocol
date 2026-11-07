# Rogue vendor audit findings

Scope: synthetic Maplewood fixtures and the course's local A2A boundaries.
Run the reference solution to reproduce each outcome; the capstone test fails if
any attack succeeds. These are exercised defects to look for, not claims about
a deployed third-party service.

| ID | Severity | Attack and impact | Hardened result and fix |
|---|---|---|---|
| AUD-01 | High | Alter a skill description to request credentials | Trusted-key signature verification rejects changed canonical bytes |
| AUD-02 | High | Fetch cloud metadata through an allowed file URL | Public-address policy rejects link-local destinations even when allow-listed |
| AUD-03 | High | Replay an authentic webhook to repeat processing | HMAC, freshness and nonce checks accept once and reject replay |
| AUD-04 | High | Read another subject's task by knowing its ID | Owner enforcement returns 404 |
| AUD-05 | High | Forward the user's token and private notes to a vendor | Captured delegation contains only allowed fields and the vendor's own credential |
| AUD-06 | High | Put spending instructions in a cheap quote artifact | Closed quote schema rejects the artifact; spending still requires human approval |

The residual risks are operational: replay history is in memory, file fetching
requires deployment-specific egress controls, and production identities and key
rotation require an operator. A signature establishes who supplied bytes; it does
not make those bytes safe instructions. Even trusted vendors' artifacts stay data.
