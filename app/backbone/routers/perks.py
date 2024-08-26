import os
from typing import TYPE_CHECKING

import requests
from backbone.config import endp
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, filter_with_text, get_req
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Character, Perk
from constants import ICONS_FOLDER
from dbdie_ml.schemas.predictables import PerkCreate, PerkOut
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import FileResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_perks(text: str = "", db: "Session" = Depends(get_db)):
    query = db.query(Perk)
    if text != "":
        query = filter_with_text(query, text, use_model="perk")
    return query.count()


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


@router.get("/{id}/image")
def get_perk_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"perks/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Perk image", id)
    return FileResponse(path)


@router.post("", response_model=PerkOut)
def create_perk(perk: PerkCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(perk.name) is None:
        raise ValidationException("Perk name can't be empty")

    assert (
        requests.get(endp(f"/characters/{perk.character_id}")).status_code
        == status.HTTP_200_OK
    )

    new_perk = {"id": requests.get(endp("/perks/count")).json()} | perk.model_dump()
    new_perk = Perk(**new_perk)

    db.add(new_perk)
    db.commit()
    db.refresh(new_perk)

    return get_req("perks", new_perk.id)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_perk(id: int, perk: PerkCreate, db: "Session" = Depends(get_db)):
    perk_query = db.query(Perk).filter(Perk.id == id)
    present_perk = perk_query.first()
    if present_perk is None:
        raise ItemNotFoundException("Perk", id)

    new_info = {"id": id} | perk.model_dump()
    character = get_req("characters", new_info["character_id"])
    character["is_for_killer"] = character["is_killer"]

    new_info = Perk(**new_info)
    perk_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
