# Tier 3: desk reference

**Authentication and authorization** — Authentication proves identity; authorization decides what that identity may do. A card advertises schemes but does not issue credentials. Obtain API keys or OAuth tokens out of band. A JWT is signed claims, not proof until issuer, audience, signature and expiration are checked. OpenID Connect adds identity discovery to OAuth. TLS protects the connection; mutual TLS also verifies a client certificate.

**Trust, signed cards and multi-tenancy** — A signature detects changes to a card and binds it to a key you already trust. Canonical JSON makes equivalent objects produce the same signed bytes. JWS specifies how headers and payload are signed. A JWKS is a set of public keys; a key URL advertised by an attacker is not automatically trusted. Tenant routing is separate from authenticated ownership.

**Security threats and defenses** — Treat cards, messages and artifacts as untrusted inputs. Prompt injection attempts to turn those inputs into higher-priority instructions. Allow-list destinations, validate outputs, keep tokens scoped, and require human approval before spending. Private-address filtering alone does not prevent DNS rebinding; use a controlled egress path or inline files. Limit bytes, duration, concurrency and tool steps.

Practice: uv run gym list --module NN; uv run gym next; uv run gym drill.
