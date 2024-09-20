"""Router code for DBD perks."""

from typing import TYPE_CHECKING

import requests
from dbdie_ml.schemas.predictables import PerkCreate, PerkOut
from fastapi import APIRouter, Depends, status

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    dbd_version_str_to_id,
    do_count,
    endp,
    get_icon,
    get_req,
    update_one,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Character, Perk
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_perks(
    is_for_killer: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count DBD perks."""
    return do_count(Perk, text, db, is_for_killer)


@router.get("", response_model=list[PerkOut])
def get_perks(
    is_for_killer: bool | None = None,
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Get many DBD perks."""
    perks = db.query(
        Perk.id,
        Perk.name,
        Perk.character_id,
        Perk.dbd_version_id,
        Perk.emoji,
        Character.is_killer.label("is_for_killer"),
    ).join(Character)
    if is_for_killer is not None:
        perks = perks.filter(Character.is_killer == is_for_killer)
    perks = perks.limit(limit)
    if skip > 0:
        perks = perks.offset(skip)

    perks = perks.all()
    return perks


@router.get("/{id}", response_model=PerkOut)
def get_perk(id: int, db: "Session" = Depends(get_db)):
    """Get a specific DBD perk with an ID."""
    perk = (
        db.query(
            Perk.id,
            Perk.name,
            Perk.character_id,
            Perk.dbd_version_id,
            Perk.emoji,
            Character.is_killer.label("is_for_killer"),
        )
        .join(Character)
        .filter(Perk.id == id)
        .first()
    )
    if perk is None:
        raise ItemNotFoundException("Perk", id)
    return perk


@router.get("/{id}/icon")
def get_perk_icon(id: int):
    """Get a DBD perk icon."""
    return get_icon("perks", id)


@router.post("", response_model=PerkOut)
def create_perk(perk: PerkCreate, db: "Session" = Depends(get_db)):
    """Create a DBD perk."""
    if NOT_WS_PATT.search(perk.name) is None:
        raise ValidationException("Perk name can't be empty")

    assert (
        requests.get(endp(f"{EP.CHARACTER}/{perk.character_id}")).status_code
        == status.HTTP_200_OK
    )

    new_perk = {"id": requests.get(endp(f"{EP.PERKS}/count")).json()} | perk.model_dump()
    new_perk["dbd_version_id"] = (
        dbd_version_str_to_id(new_perk["dbd_version_str"])
        if new_perk["dbd_version_str"] is not None
        else None
    )
    del new_perk["dbd_version_str"]
    new_perk = Perk(**new_perk)

    add_commit_refresh(new_perk, db)

    return get_req(EP.PERKS, new_perk.id)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_perk(id: int, perk: PerkCreate, db: "Session" = Depends(get_db)):
    """Update the information of a DBD perk."""
    return update_one(perk, Perk, "Perk", id, db)
