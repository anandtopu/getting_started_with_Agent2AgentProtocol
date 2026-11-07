"""Deterministic vendor work. Money uses integer cents, never model arithmetic."""

from common.data import load


def quote(vendor: str, brief: dict, *, partner: bool = False) -> dict:
    guests = brief.get("guests", 40)
    if (
        isinstance(guests, bool)
        or not isinstance(guests, (int, float))
        or int(guests) != guests
        or not 1 <= guests <= 1000
    ):
        raise ValueError("guests must be a whole number between 1 and 1000")
    guests = int(guests)
    if vendor == "venues":
        choices = [
            v
            for v in load("venues.json")
            if v["capacity"] >= guests
            and v["availability"].get(brief.get("date", "2027-06-01"), False)
        ]
        if not choices:
            raise ValueError("No available room has sufficient capacity.")
        item = min(choices, key=lambda v: v["price_cents"])
        amount, selection = item["price_cents"], item["id"]
    elif vendor == "catering":
        dietary = brief.get("dietary")
        if not isinstance(dietary, dict) or sum(dietary.values()) != guests:
            raise ValueError("Dietary counts must sum to guests.")
        if any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 or int(v) != v
            for v in dietary.values()
        ):
            raise ValueError("Dietary counts must be nonnegative whole numbers.")
        item = load("menus.json")[0]
        amount, selection = guests * item["price_cents"], item["id"]
    elif vendor == "av":
        items = load("av_inventory.json")
        amount = sum(item["price_cents"] for item in items)
        selection = ", ".join(item["id"] for item in items)
    elif vendor == "travel":
        rooms = brief.get("rooms", max(1, guests // 2))
        if (
            isinstance(rooms, bool)
            or not isinstance(rooms, (int, float))
            or rooms < 1
            or int(rooms) != rooms
        ):
            raise ValueError("rooms must be a positive whole number")
        choices = [h for h in load("hotels.json") if h["room_block"] >= rooms]
        if not choices:
            raise ValueError("No hotel has enough rooms.")
        item = choices[0]
        amount, selection = (
            int(rooms) * item["partner_cents" if partner else "public_cents"],
            item["id"],
        )
    elif vendor == "print":
        item = load("print_products.json")[0]
        amount, selection = guests * item["price_cents"], item["id"]
    else:
        raise ValueError(f"Unknown vendor: {vendor}")
    return {
        "vendor": vendor,
        "selection": selection,
        "currency": "USD",
        "total_cents": amount,
        "guests": guests,
        "approved": False,
    }
