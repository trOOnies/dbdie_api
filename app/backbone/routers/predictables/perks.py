"""Router code for perks"""

from typing import TYPE_CHECKING

import requests
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    dbd_version_str_to_id,
    do_count,
    endp,
    filter_one,
    get_icon,
    get_req,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Character, Perk
from dbdie_ml.schemas.predictables import PerkCreate, PerkOut
from fastapi import APIRouter, Depends, Response, status

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_perks(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(Perk, text, db)


@router.get("", response_model=list[PerkOut])
def get_perks(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    perks = (
        db.query(
            Perk.id,
            Perk.name,
            Perk.character_id,
            Perk.dbd_version_id,
            Character.is_killer.label("is_for_killer"),
        )
        .join(Character)
        .limit(limit)
    )
    if skip > 0:
        perks = perks.offset(skip)
    perks = perks.all()
    return perks


@router.get("/{id}", response_model=PerkOut)
def get_perk(id: int, db: "Session" = Depends(get_db)):
    perk = (
        db.query(
            Perk.id,
            Perk.name,
            Perk.character_id,
            Perk.dbd_version_id,
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
    return get_icon("perks", id)


@router.post("", response_model=PerkOut)
def create_perk(perk: PerkCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(perk.name) is None:
        raise ValidationException("Perk name can't be empty")

    assert (
        requests.get(endp(f"/characters/{perk.character_id}")).status_code
        == status.HTTP_200_OK
    )

    new_perk = {"id": requests.get(endp("/perks/count")).json()} | perk.model_dump()
    new_perk["dbd_version_id"] = (
        dbd_version_str_to_id(new_perk["dbd_version_str"])
        if new_perk["dbd_version_str"] is not None
        else None
    )
    del new_perk["dbd_version_str"]
    new_perk = Perk(**new_perk)

    add_commit_refresh(new_perk, db)

    return get_req("perks", new_perk.id)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_perk(id: int, perk: PerkCreate, db: "Session" = Depends(get_db)):
    _, perk_query = filter_one(Perk, "Perk", id, db)

    new_info = {"id": id} | perk.model_dump()
    character = get_req("characters", new_info["character_id"])
    character["is_for_killer"] = character["is_killer"]

    new_info = Perk(**new_info)
    perk_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
