# Official TCK execution and manual evidence

The official suite is executed unmodified at revision
`70f6f73c30208e80c889141907e094899e6e9f05`. The next upstream revision requires
Python 3.15; this pinned revision runs with Python 3.13 and the released protocol.
The fixture uses the TCK-generated executor through the course's official SDK
transport policies. Vendor business behavior is checked separately by the golden,
contract, security and recovery suites. This is not a conformance certification.

~~~console
uv run python scripts/check_tck.py
~~~

First setup downloads the official repository and its locked dependencies. The
suite uses real loopback HTTP/gRPC servers, so it is an explicit integration job,
not part of the no-network gym. It generates all sixteen fixture scenarios and
runs JSON-RPC, HTTP+JSON and gRPC. Source modifications cause the runner to fail.

The recorded run has **263 cases: 202 passed, 57 skipped, four failed, zero errors**.
Its automated requirement score is **79.6%**, which is not a percentage of test
cases and does not include manual verification. Skips include optional capabilities
not advertised by this fixture. Raw reports remain in workspace/a2a-tck/reports
and the official-tck-evidence CI artifact. The raw upstream exit code remains 1.

## Four reviewed upstream contradictions

| Case | Observed behavior | Why the implementation is retained |
|---|---|---|
| test_error_uses_aip193_format | Requires application/json for an HTTP error | The same suite's HTTP_JSON-SVC-001 requires application/a2a+json; the error body still uses google.rpc.Status |
| CORE-SEND-003, JSON-RPC | Reports required ContentTypeNotSupportedError as an operation failure | Rejecting the unsupported media type is the requirement being exercised |
| CORE-SEND-003, HTTP+JSON | Reports the required HTTP 400 as an operation failure | The required rejection must not be replaced with a success response |
| CORE-SEND-003, gRPC | Reports the required unsupported-media status as failure | All bindings retain the same rejection semantics |

The regression gate permits only these exact case names **and diagnostic messages**.
An unexpected failure, error, empty test run, or infrastructure exit fails CI.
Green TCK regression CI means this reviewed baseline did not regress; it does not
mean that all official assertions passed. See the [pinned official source](https://github.com/a2aproject/a2a-tck/tree/70f6f73c30208e80c889141907e094899e6e9f05)
and the [normative specification](https://a2a-protocol.org/v1.0.1/specification/).

## Manual requirements

| Requirement | Review evidence |
|---|---|
| CARD-CLIENT-001 | Configured interface/tenant routing and rejected foreign tenants: common/remote.py, common/security.py, tests/test_security.py |
| CARD-SIGN-001 | JWS signing input canonicalizes the unsigned card with JCS: common/security.py and tests/test_security.py |
| CARD-SIGN-002 | Protected algorithm and key ID; reject unsupported algorithm, critical headers and attacker key URLs: verify_card |
| CARD-SIGN-003 | Out-of-band keys or operator-pinned HTTPS JWKS; no self-appointed trust: common/card_trust.py |
| CARD-SIGN-004 | Rotation, overlap, expiration, revocation and replica/restart agreement: tests/test_auth_profiles.py and tests/test_shared_keys.py |
| AUTH-TLS-001 | Actual HTTPS and gRPC TLS with hostname/CA validation: scripts/check_tls.py and scripts/check_hardened.py |
| AUTH-TLS-002 | Reject missing mTLS client certificate and untrusted server CA; verified on all three operating systems |
| AUTH-SERVER-001 | Enforce authentication before operations; cross-audience, scope and tenant checks: tests/test_identity.py, tests/test_auth_profiles.py, hardened Compose |
| BIND-CUSTOM-002 | Not applicable: the course defines an extension URI, but no custom protocol binding |

These manual observations supplement the raw suite; they do not change its score
or convert skipped requirements into upstream passes.
