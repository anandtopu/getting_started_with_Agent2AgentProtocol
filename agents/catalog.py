"""Explicit skill contracts, not instructions inferred from untrusted descriptions."""

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentExtension,
    AgentInterface,
    AgentProvider,
    AgentSkill,
    HTTPAuthSecurityScheme,
    SecurityRequirement,
    SecurityScheme,
    StringList,
)

from common.config import grpc_target, url

NAMES = {
    "venues": "Granite Hall Venues",
    "catering": "Saffron Table Catering",
    "av": "Brightline AV",
    "travel": "Northstar Travel Desk",
    "print": "Inkwell Print Co.",
    "concierge": "Maplewood Concierge",
}
CONTRACTS = {
    "venues": "Find an available room for a date and guest count; return capacity and a quote in cents. No purchase.",
    "catering": "Quote a menu for a guest count and dietary breakdown; ask for missing dietary counts. No purchase.",
    "av": "Produce an equipment plan and stream it in ordered chunks; return a quote in cents. No purchase.",
    "travel": "Quote room blocks; partner scope unlocks negotiated pricing. No reservations without approval.",
    "print": "Quote badges and signs from a structured brief and optional inline artwork. No print order.",
    "concierge": "Collect quotes from allow-listed vendors and surface missing inputs. Never spend without approval.",
}
QUOTE_EXTENSION = "https://maplewood.example/extensions/structured-quote/v1"


def card(
    vendor: str, *, secure: bool = True, extended: bool = False, grpc_only: bool = False
) -> AgentCard:
    interfaces = [
        AgentInterface(
            url=url(vendor) + "/rpc", protocol_binding="JSONRPC", protocol_version="1.0"
        ),
        AgentInterface(url=url(vendor), protocol_binding="HTTP+JSON", protocol_version="1.0"),
    ]
    if grpc_only:
        interfaces = [
            AgentInterface(url=grpc_target(), protocol_binding="GRPC", protocol_version="1.0")
        ]
    result = AgentCard(
        name=NAMES[vendor],
        description=CONTRACTS[vendor],
        version="1.0.0",
        provider=AgentProvider(organization=NAMES[vendor], url="https://maplewood.example"),
        supported_interfaces=interfaces,
        capabilities=AgentCapabilities(
            streaming=True,
            extended_agent_card=vendor == "travel",
            extensions=[AgentExtension(uri=QUOTE_EXTENSION, required=False)],
        ),
        default_input_modes=["text/plain", "application/json", "application/octet-stream"],
        default_output_modes=["application/json", "text/plain"],
        skills=[
            AgentSkill(
                id=f"{vendor}.quote",
                name=f"{NAMES[vendor]} quote",
                description=CONTRACTS[vendor],
                tags=["events", vendor],
                examples=["Quote a 40-person offsite on 2027-06-01"],
            )
        ],
    )
    if secure:
        result.security_schemes["vendor_token"].CopyFrom(
            SecurityScheme(http_auth_security_scheme=HTTPAuthSecurityScheme(scheme="Bearer"))
        )
        result.security_requirements.append(
            SecurityRequirement(schemes={"vendor_token": StringList()})
        )
    if extended:
        result.skills.append(
            AgentSkill(
                id="travel.partner_quote",
                name="Partner hotel prices",
                description="Negotiated room rates for authenticated partners.",
                tags=["partner"],
            )
        )
    return result
