"""Extra code for the '/character' endpoints."""

import requests
from backbone.endpoints import endp, parse_or_raise
from backbone.options import ENDPOINTS as EP

ADDON_TYPE_ID = 1


def create_perks(character: dict, perk_names: list[str]) -> list[dict]:
    """Perks creation for use in FullCharacterCreate."""
    perks = []
    for perk_name in perk_names:
        p = requests.post(
            endp(EP.PERKS),
            json={
                "name": perk_name,
                "character_id": character["id"],
                "dbd_version_id": character["dbd_version_id"],
            },
        )
        perks.append(parse_or_raise(p))

    return perks


def create_addons(
    character: dict,
    addon_names: list[str] | None,
) -> list[dict] | None:
    """Addons creation for use in FullCharacterCreate."""
    if addon_names is None:
        addons = None
    else:
        addons = []
        for addon_name in addon_names:
            a = requests.post(
                endp(EP.ADDONS),
                json={
                    "name": addon_name,
                    "type_id": ADDON_TYPE_ID,
                    "user_id": character["id"],
                    "dbd_version_id": character["dbd_version_id"],
                },
            )
            addons.append(parse_or_raise(a))

    return addons


def create_killer_power(power_name: str | None) -> dict | None:
    """Killer power creation for use in FullCharacterCreate."""
    return (
        None if power_name is None
        else parse_or_raise(
            requests.post(
                endp(EP.ITEM),
                json={
                    "name": power_name,
                    "type_id": 1,  # * Killer power id
                },
            )
        )
    )
