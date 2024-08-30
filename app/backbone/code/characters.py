from typing import Optional

import requests
from backbone.endpoints import endp

ADDON_TYPE_ID = 1


def create_perks_and_addons(
    character: dict,
    perk_names: list[str],
    addon_names: Optional[list[str]],
) -> tuple[list[dict], list[dict]]:
    perks = []
    for perk_name in perk_names:
        p = requests.post(
            endp("/perks"),
            json={"name": perk_name, "character_id": character["id"]},
        )
        perks.append(p.json())

    addons = []
    if addon_names is not None:
        for addon_name in addon_names:
            a = requests.post(
                endp("/addons"),
                json={
                    "name": addon_name,
                    "type_id": ADDON_TYPE_ID,
                    "user_id": character["id"],
                },
            )
            addons.append(a.json())

    return perks, addons
