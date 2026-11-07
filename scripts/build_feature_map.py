"""Build a navigable coverage contract from real files and installed protobuf symbols."""

import json

from a2a.types import a2a_pb2

from common.config import ROOT

SPEC = "https://a2a-protocol.org/v1.0.1/specification/"
PROTO = "https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto"


def link(path, label=None):
    return f"[{label or path.name}](../{path.relative_to(ROOT).as_posix()})"


def main():
    modules = json.loads((ROOT / "common/course_catalog.json").read_text())
    folders = {
        m["id"]: ROOT
        / "modules"
        / ("bonus" if m["id"].startswith("B") else "")
        / (m["id"] + "_" + m["slug"])
        for m in modules
    }
    rows = [
        "# Coverage contract",
        "",
        "Targets specification 1.0.1 and Python SDK 1.3.0. Each teaching path below",
        "links to executable files, its use case and graded work. Schema inspection",
        "is distinguished from a complete operational implementation.",
        "",
        "## Module paths",
        "",
        "| Area | Module | Runnable examples | Use case | Graded tasks |",
        "|---|---|---|---|---|",
    ]
    for module in modules:
        folder = folders[module["id"]]
        examples = ", ".join(link(p, p.stem) for p in sorted((folder / "examples").glob("*.py")))
        tasks = ", ".join(
            link(p / "task.md", p.name.split("_")[0])
            for p in sorted((ROOT / "gym/tasks" / module["id"]).iterdir())
            if p.is_dir()
        )
        rows.append(
            f"| {module['title']} | {link(folder / 'README.md', module['id'])} | "
            f"{examples} | {link(folder / 'use_case/run.py', 'Run')} | {tasks} |"
        )
    rows += [
        "",
        "## Normative operation coverage",
        "",
        "Each wire link contains actual requests and responses in all three bindings;",
        "gRPC captures are protobuf service-boundary calls. SubscribeToTask on a",
        "terminal task deliberately records a protocol error, not successful reconnect.",
        "",
        "| Operation (a2a.proto service symbol) | Three-binding captures | Teaching path |",
        "|---|---|---|",
    ]
    service = a2a_pb2.DESCRIPTOR.services_by_name["A2AService"]
    for operation in service.methods:
        captures = sorted((ROOT / "docs/wire").glob("*-operations.jsonl"))
        rows.append(
            f"| [{operation.name}]({PROTO}) | "
            + ", ".join(link(p, p.stem) for p in captures)
            + f" | {link(ROOT / 'docs/OPERATIONS_ON_THE_WIRE.md', 'Binding walkthrough')} |"
        )
    groups = {
        "02": {"AgentCard", "AgentInterface", "AgentProvider", "AgentCapabilities", "AgentSkill"},
        "05": {"Task", "TaskStatus", "TaskState", "GetTaskRequest", "CancelTaskRequest"},
        "06": {"Part", "Message", "Artifact", "Role"},
        "07": {
            "TaskStatusUpdateEvent",
            "TaskArtifactUpdateEvent",
            "TaskPushNotificationConfig",
            "AuthenticationInfo",
            "SubscribeToTaskRequest",
            "StreamResponse",
            "GetTaskPushNotificationConfigRequest",
            "DeleteTaskPushNotificationConfigRequest",
            "ListTaskPushNotificationConfigsRequest",
            "ListTaskPushNotificationConfigsResponse",
        },
        "04": {"SendMessageConfiguration", "SendMessageRequest", "SendMessageResponse"},
        "13": {
            "SecurityScheme",
            "SecurityRequirement",
            "StringList",
            "HTTPAuthSecurityScheme",
            "OpenIdConnectSecurityScheme",
            "GetExtendedAgentCardRequest",
            "ClientCredentialsOAuthFlow",
        },
        "14": {"AgentCardSignature"},
        "18": {"AgentExtension", "ListTasksRequest", "ListTasksResponse"},
    }
    schema_only = {
        "APIKeySecurityScheme",
        "OAuth2SecurityScheme",
        "MutualTlsSecurityScheme",
        "OAuthFlows",
        "AuthorizationCodeOAuthFlow",
        "DeviceCodeOAuthFlow",
        "ImplicitOAuthFlow",
        "PasswordOAuthFlow",
    }
    rows += [
        "",
        "## Protocol objects and enums",
        "",
        "The symbol names below come from the installed official protobuf descriptor.",
        "Follow the module row above for examples, use case and tasks.",
        "",
        "| Proto symbol | Module | Evidence and scope |",
        "|---|---|---|",
    ]
    symbols = sorted(
        set(a2a_pb2.DESCRIPTOR.message_types_by_name) | set(a2a_pb2.DESCRIPTOR.enum_types_by_name)
    )
    for symbol in symbols:
        module = next((key for key, values in groups.items() if symbol in values), "13")
        evidence = (
            "Schema and explanation only; no live implementation"
            if symbol in schema_only
            else "Executable lesson or operation capture; see module path"
        )
        if symbol in {"ImplicitOAuthFlow", "PasswordOAuthFlow"}:
            evidence = "Deprecated schema compatibility only; not recommended or exercised"
        rows.append(
            f"| [{symbol}]({PROTO}) | {link(folders[module] / 'README.md', module)} | {evidence} |"
        )
    rows += [
        "",
        "## SDK and deployment integrations",
        "",
        "| Capability | Implementation and evidence |",
        "|---|---|",
        "| Seven frameworks | [Verified runtime matrix](../integrations/README.md) |",
        "| Python / TypeScript / Go / Java / .NET preview | [Language labs](../modules/bonus/B2_other_sdks/README.md) and [TypeScript](../modules/bonus/B1_typescript/README.md) |",
        "| SQLite and PostgreSQL task recovery | [Restart tests](../tests/test_persistence.py) and [container checker](../scripts/check_compose.py) |",
        "| HTTP and gRPC traces | [Parentage tests](../tests/test_observability.py) |",
        "| Keycloak/OIDC | [Token lab](../deploy/OIDC_LAB.md) |",
        "| MCP inside A2A | [Kitchen server](../agents/kitchen.py) and [workflow](../agents/langgraph_vendor.py) |",
        "| Rogue vendors | [Six-attack audit](../capstones/03_rogue_audit/FINDINGS.md) |",
        "| Model selection | [Offline tests](../tests/test_model_planning.py) and [live configuration](LIVE_MODELS.md) |",
        "",
        "## Explicit coverage gaps",
        "",
        "Per-vendor heterogeneous authentication, production mTLS, durable multi-replica",
        "event delivery, atomic task/outbox transactions, key rotation,",
        "stream reconnect chaos, and provider-native streamed tool calls are not",
        "implemented end to end. The gym meets the module count/type/level contract;",
        "it is not six distinct full-agent exercises for every object in this table.",
        "See [the release checklist](VALIDATION_REPORT.md) for the exact validation scope.",
        "",
        f"[Specification sections]({SPEC}) · [Normative protobuf]({PROTO})",
        "",
    ]
    (ROOT / "docs/FEATURE_MAP.md").write_text("\n".join(rows), encoding="utf-8")


if __name__ == "__main__":
    main()
