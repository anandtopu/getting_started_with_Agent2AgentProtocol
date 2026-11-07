# Security checklist

## Server

- [ ] Bind local demos to 127.0.0.1; use TLS outside local development.
- [ ] Authenticate before accepting work and authorize each protected skill.
- [ ] Scope GetTask, ListTasks, cancellation and push configuration to the caller.
- [ ] Bind tenant routing to authenticated identity; never trust a tenant field alone.
- [ ] Validate types, media modes, quantities and monetary values.
- [ ] Bound body size, concurrency, duration, stored history and task count.
- [ ] Prevent accidental model/provider imports in deterministic lessons.

## Client and orchestrator

- [ ] Provision trusted destinations and keys; a discovered URL is not trusted automatically.
- [ ] Verify card signatures before relying on their identity.
- [ ] Give every vendor a separate service credential with minimal permissions.
- [ ] Do not forward the user's credential or unnecessary private fields.
- [ ] Validate artifacts against schemas and expected vendor identity.
- [ ] Treat remote descriptions and artifacts as data, never policy overrides.
- [ ] Require explicit approval before paid or irreversible work.
- [ ] Set deadlines, tool budgets, retry limits and compensation policies.

## Files and webhooks

- [ ] Reject private/reserved addresses and unapproved origins.
- [ ] Prevent DNS rebinding and redirect-based bypasses; enforce size and time limits.
- [ ] Verify callback sender, timestamp and replay identifier before processing.
- [ ] Make duplicate delivery safe; durably record accepted deliveries if needed.
- [ ] Keep callback credentials outside ordinary A2A message parts.

## Operations

- [ ] Rotate keys and tokens; pin issuer, audience and algorithms for JWT verification.
- [ ] Redact telemetry and wire captures.
- [ ] Test proxy streaming and shutdown behavior.
- [ ] Use a durable outbox for reliable callbacks and shared events for replicas.
- [ ] Exercise malicious cards, forged identities, poisoned artifacts and endless work.

This checklist is a review tool. See verification notes for which boxes the
teaching implementation actually demonstrates.
