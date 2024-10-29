"""Extra code for the '/character' endpoints."""

from typing import TYPE_CHECKING, Optional

from backbone.endpoints import postr
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from dbdie_classes.base import LabelName

ADDON_TYPE_ID = 1


def create_perks(character: dict, perk_names: list["LabelName"]) -> list[dict]:
    """Perks creation for use in FullCharacterCreate."""
    perks = []
    for perk_name in perk_names:
        p = postr(
            EP.PERKS,
            json={
                "name": perk_name,
                "character_id": character["id"],
                "dbdv_id": character["dbdv_id"],
            },
        )
        perks.append(p)

    return perks


def create_addons(
    character: dict,
    addon_names: list["LabelName"] | None,
) -> list[dict] | None:
    """Addons creation for use in FullCharacterCreate."""
    if addon_names is None:
        addons = None
    else:
        addons = []
        for addon_name in addon_names:
            a = postr(
                EP.ADDONS,
                json={
                    "name": addon_name,
                    "type_id": ADDON_TYPE_ID,
                    "user_id": character["id"],  # TODO
                    "dbdv_id": character["dbdv_id"],
                },
            )
            addons.append(a)

    return addons


def create_killer_power(power_name: Optional["LabelName"]) -> dict | None:
    """Killer power creation for use in FullCharacterCreate."""
    return (
        None if power_name is None
        else postr(
            EP.ITEM,
            json={
                "name": power_name,
                "type_id": 1,  # * Killer power id
            },
        )
    )
