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

First setup downloads the official repository and installs its committed dependency
lock with `uv sync --frozen --python 3.13`. At this revision, `pyproject.toml`
has a `<3.15` upper bound absent from `uv.lock`; both permit 3.13. The former
plain `uv sync` rewrote that lock metadata. Frozen installation preserves all
committed dependency versions and leaves the upstream checkout unchanged. The
suite uses real loopback HTTP/gRPC servers, so it is an explicit integration job,
not part of the no-network gym. It generates all sixteen fixture scenarios and
runs JSON-RPC, HTTP+JSON and gRPC. Source modifications cause the runner to fail.

The recorded run has **263 cases: 202 passed, 57 skipped, four failed, zero errors**.
Its automated requirement score is **79.6%**, which is not a percentage of test
cases and does not include manual verification. Skips include optional capabilities
not advertised by this fixture. Raw reports remain in workspace/a2a-tck/reports
and the official-tck-evidence CI artifact. The raw upstream exit code remains 1.

## Four reviewed upstream exceptions

| Case | Observed behavior | Why the implementation is retained |
|---|---|---|
| test_error_uses_aip193_format | Requires application/json for an HTTP error | Specification 11.1 recommends application/a2a+json, and 11.6 demonstrates it for errors; the body retains the required structured error |
| CORE-SEND-003, JSON-RPC | Reports required ContentTypeNotSupportedError as an operation failure | Rejecting the unsupported media type is the requirement being exercised |
| CORE-SEND-003, HTTP+JSON | Reports the required HTTP 400 as an operation failure | The required rejection must not be replaced with a success response |
| CORE-SEND-003, gRPC | Reports the required unsupported-media status as failure | All bindings retain the same rejection semantics |

The regression gate permits only the reviewed **class, case name and complete
diagnostic message**, with exactly one failure element and no error/skip element.
It requires 263 distinct cases, matching JUnit counters, no more than 57 skips,
execution of all four affected cases, and an exit status consistent with the
raw outcomes. Genuine passes are accepted without requiring an exception to fail.
An unexpected failure, infrastructure error, partial run or extra skip fails CI.
Old generated evidence is cleared before setup; readiness has a hard failure;
the upstream tracked tree is checked both before installation and after execution.
Green TCK regression CI means this reviewed baseline did not regress; it does not
mean that all official assertions passed. See the [pinned official source](https://github.com/a2aproject/a2a-tck/tree/70f6f73c30208e80c889141907e094899e6e9f05)
and the [normative specification](https://a2a-protocol.org/v1.0.1/specification/).

### Source-level investigation

The HTTP assertion in
[test_error_handling.py](https://github.com/a2aproject/a2a-tck/blob/70f6f73c30208e80c889141907e094899e6e9f05/tests/compatibility/core_operations/test_error_handling.py#L762)
checks for the literal substring `application/json` and only inspects the error
body in its `else` branch. This rejects `application/a2a+json` before validating
the body. The media type recommendation is **SHOULD**, not MUST; our previous
report overstated its requirement level. Changing the server to satisfy this
assertion would abandon the recommended type and fail the suite's separate
media-type check. We retain the recommended type and validate the body independently.

The three CORE-SEND-003 failures share one cause:
[the requirement definition](https://github.com/a2aproject/a2a-tck/blob/70f6f73c30208e80c889141907e094899e6e9f05/tck/requirements/core_operations.py#L99)
provides the unsupported-media request but omits `expected_error`. The
[generic response validator](https://github.com/a2aproject/a2a-tck/blob/70f6f73c30208e80c889141907e094899e6e9f05/tests/compatibility/core_operations/test_requirements.py#L100)
therefore falls through to a success check and rejects the required error.
The course handler already enables the SDK's `validate_input_modes=True`; no
executor-specific success response or media acceptance workaround is appropriate.

Upstream head `104a7b4ae0d83f65c075e3793e322953a830eaba` was also inspected:
[the comparison](https://github.com/a2aproject/a2a-tck/compare/70f6f73c30208e80c889141907e094899e6e9f05...104a7b4ae0d83f65c075e3793e322953a830eaba)
changes only `pyproject.toml` and `uv.lock`, requires Python 3.15+, and does not
repair either test defect. The compatible revision remains pinned. No upstream
test, requirement metadata or generated executor is patched by the course.

### Independent obligations, without score substitution

[scripts/tck_evidence.py](../scripts/tck_evidence.py) runs against the same real
HTTP/gRPC fixture before the official suite. Failure of any control stops the job:

| Control | Required observed evidence |
|---|---|
| Missing HTTP task | HTTP 404, recommended content type, structured code/status/message, TASK_NOT_FOUND ErrorInfo and A2A domain |
| Unsupported HTTP part | HTTP 400, recommended content type, INVALID_ARGUMENT status, CONTENT_TYPE_NOT_SUPPORTED ErrorInfo and A2A domain |
| Unsupported JSON-RPC part | Matching JSON-RPC version/request ID, code -32005, nonempty message, no success result; validate typed details when present |
| Unsupported gRPC part | INVALID_ARGUMENT, binary google.rpc.Status matching transport code/message, CONTENT_TYPE_NOT_SUPPORTED ErrorInfo and A2A domain |

The CI artifact now includes `tck-wire-evidence.json` (HTTP headers/status/body
and decoded plus encoded gRPC details) and the fixture log alongside the untouched
official reports. These four independent passes do **not** turn the four official
failures into passes or change the upstream score. The ordinary vendor handler
also exercises these errors in [transport tests](../tests/test_binding_policy.py).
[Mutation controls](../tests/test_tck_gate.py) reject incorrect status, identity,
content type, details, diagnostics and report completeness.

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
