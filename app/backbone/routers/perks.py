import os
import requests
from dbdie_ml.schemas.predictables import Perk, PerkCreate
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, status, Response
from fastapi.responses import FileResponse

from constants import ICONS_FOLDER
from backbone import models
from backbone.config import endp
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, req_wrap, filter_with_text
from backbone.exceptions import ItemNotFoundException

router = APIRouter()


@router.get("/count", response_model=int)
def count_perks(text: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Perk)
    if text != "":
        query = filter_with_text(query, text, use_model="perk")
    return query.count()


@router.get("", response_model=list[Perk])
def get_perks(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    perks = (
        db.query(
            models.Perk.id,
            models.Perk.name,
            models.Perk.character_id,
            models.Perk.dbd_version_id,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .limit(limit)
    )
    if skip > 0:
        perks = perks.offset(skip)
    perks = perks.all()
    return perks


@router.get("/{id}", response_model=Perk)
def get_perk(id: int, db: "Session" = Depends(get_db)):
    perk = (
        db.query(
            models.Perk.id,
            models.Perk.name,
            models.Perk.character_id,
            models.Perk.dbd_version_id,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .filter(models.Perk.id == id)
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


@router.post("", response_model=Perk)
def create_perk(perk: PerkCreate, db: Session = Depends(get_db)):
    if NOT_WS_PATT.search(perk.name) is None:
        return status.HTTP_400_BAD_REQUEST

    req_wrap("characters", perk.character_id)

    new_perk = perk.model_dump()
    new_perk = {"id": requests.get(endp("/perks/count")).json()} | new_perk
    new_perk = models.Perk(**new_perk)

    db.add(new_perk)
    db.commit()
    db.refresh(new_perk)

    return req_wrap("perks", new_perk.id)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_perk(id: int, perk: PerkCreate, db: "Session" = Depends(get_db)):
    new_info = perk.model_dump()

    perk_query = db.query(models.Perk).filter(models.Perk.id == id)
    present_perk = perk_query.first()
    if present_perk is None:
        raise ItemNotFoundException("Perk", id)

    new_info = {"id": id} | new_info
    character = requests.get(endp(f"/characters/{new_info['character_id']}"))
    if character.status_code != 200:
        raise ItemNotFoundException("Perk", id)
    character = character.json()
    character["is_for_killer"] = character["is_killer"]

    perk_query.update(new_info, synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)
