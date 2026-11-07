# 03-06: Design a partner contract and failure policy

**Type:** design · **Level:** hard

Maplewood is preparing a 40-person offsite. Practice your first a2a server at its vendor boundary.

## Requirements and acceptance criteria

Write design.md with the six rubric sections below. Automated checking covers structure only; a human must judge quality.

## Human rubric (0–2 per dimension)

- **Boundaries**: 0 absent; 1 described; 2 concrete, testable and justified for this scenario.
- **Skills**: 0 absent; 1 described; 2 concrete, testable and justified for this scenario.
- **Task flow**: 0 absent; 1 described; 2 concrete, testable and justified for this scenario.
- **Trust**: 0 absent; 1 described; 2 concrete, testable and justified for this scenario.
- **Failures**: 0 absent; 1 described; 2 concrete, testable and justified for this scenario.
- **Tradeoffs**: 0 absent; 1 described; 2 concrete, testable and justified for this scenario.

Proficient: 10/12 with no zero in Trust or Failures. Record reviewer and evidence; word count is not proficiency.

## Spec sections

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Normative protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Run uv run gym start 03-06, edit the copied files, then uv run gym check 03-06.

**Security question:** What could a malicious peer send here, and where must you reject it?
