# Delivery plan and assumptions

The user authorized all seven phases without intermediate approval on 2026-11-07.
The workspace was empty. Python 3.11–3.13 and an editable package let examples run
by path on PowerShell, macOS and Linux.

1. Verify the specification, migration guide, protobuf and package releases.
2. Implement shared deterministic vendors, configuration, data and an offline gym.
3. Build foundations with actual HTTP exchanges and a protobuf service harness.
4. Add scripted model decisions and a bounded orchestrator.
5. Add authentication, signing and attack-oriented checks.
6. Add observability, persistence and deployment materials.
7. Add bonus integrations, capstones and references; validate and publish.

The [task list](GYM_TASKS.md), [feature map](FEATURE_MAP.md) and
[learning path](../LEARNING_PATH.md) are detailed planning artifacts.

## Verified baseline and corrections

The stable specification observed was 1.0.1; its interface version is 1.0.
Python and JavaScript SDK package versions are 1.3.0. See the dated version table
in [verification notes](VERIFICATION_NOTES.md).

The well-known card path and signatures already appeared before version 1.
Version 1 establishes the proto-first contract, unified Part values, uppercase
enum strings, current operation names, per-interface protocol versions and
member-based streaming wrappers. Resolve overview discrepancies against protobuf.

## Repository structure

~~~text
README.md                 Entry point and quick start
LEARNING_PATH.md           Tiers, schedules and checkpoints
pyproject.toml / uv.lock   Python package and dependency resolution
package.json              Optional TypeScript tooling
common/                   Protocol, lessons, models, trust and testing
agents/                   Vendor and Concierge implementations
data/                     Inventory, 20 events and attack fixtures
modules/00_* to 20_*/      Lessons, examples, notebooks, captures and tests
modules/bonus/B1_* to B4_* Optional ecosystem introductions
gym/                      CLI, grading and 265 task folders
workspace/                Ignored attempts, local tokens and progress
control_room/             Streamlit network viewer
capstones/                Specifications, starters, references and rubrics
deploy/                   Container and service configuration
cheatsheets/               Tier and protocol reference sheets
docs/                     Guides, verification and coverage
scripts/                  Data, network, capture and validation tools
tests/                    Contracts, security and repository checks
.github/                  CI and contribution templates
~~~

## Completion rule

Executed checks and unexecuted integrations are reported separately. A folder and
passing smoke test do not prove exhaustive feature coverage. The [validation report](VALIDATION_REPORT.md) records completed advanced integrations
and the remaining external SDK/TCK limitations.
