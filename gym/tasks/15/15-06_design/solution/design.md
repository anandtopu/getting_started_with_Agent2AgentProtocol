# Maplewood decision: Security threats and defenses

## Boundaries
Maplewood owns coordination and budget approval. The vendor owns inventory and quote production. Keep the external A2A boundary where independent ownership or deployment requires it; use local functions for tightly coupled validation.

## Skills
Expose one quote skill with a stable identifier, required guest count, date and documented currency. Reject unsupported inputs. Return a structured deliverable instead of asking callers to extract money from prose.

## Task flow
Create a task for tracked work, report working, then complete with an artifact or pause for missing information. Preserve vendor task and context identifiers in the Concierge conversation mapping when continuing.

## Trust
Authenticate calls using a vendor-scoped service credential in a header. Verify card signatures against provisioned keys, restrict destinations, minimize brief fields, and never promote remote descriptions into orchestration instructions.

## Failures
Apply a deadline and tool budget. Report partial results with the responsible vendor. Retry only safe operations and compensate confirmed holds explicitly. Require approval before a quote becomes a paid commitment.

## Tradeoffs
Independent services add latency, deployment work and distributed failure modes. Their ownership and interoperability benefits justify them for external vendors; a single process is cheaper for a small internal prototype with shared lifecycle requirements.
