import os
import requests
from dbdie_ml import schemas
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from constants import ICONS_FOLDER
from backbone import models
from backbone.config import ST
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, req_wrap, filter_with_text

router = APIRouter(prefix="/perks", tags=["perks"])


@router.get("/count", response_model=int)
def count_perks(text: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Perk)
    if text != "":
        query = filter_with_text(query, text, use_model="perk")
    return query.count()


@router.get("", response_model=list[schemas.Perk])
def get_perks(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    perks = (
        db.query(
            models.Perk.id,
            models.Perk.name,
            models.Perk.character_id,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .limit(limit)
    )
    if skip > 0:
        perks = perks.offset(skip)
    perks = perks.all()
    return perks


@router.get("/{id}", response_model=schemas.Perk)
def get_perk(id: int, db: "Session" = Depends(get_db)):
    perk = (
        db.query(
            models.Perk.id,
            models.Perk.name,
            models.Perk.character_id,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .filter(models.Perk.id == id)
        .first()
    )
    if perk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"perk with id {id} was not found",
        )
    return perk


@router.get("/{id}/image")
def get_perk_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"perks/{id}.png")
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"perk image with id {id} was not found",
        )
    return FileResponse(path)


@router.post("", response_model=schemas.Perk)
def create_perk(perk: schemas.PerkCreate, db: Session = Depends(get_db)):
    if NOT_WS_PATT.search(perk.name) is None:
        return status.HTTP_400_BAD_REQUEST

    req_wrap("characters", perk.character_id)

    new_perk = perk.model_dump()
    new_perk["id"] = requests.get(f"{ST.fastapi_host}/perks/count").json()
    new_perk = models.Perk(**new_perk)

    db.add(new_perk)
    db.commit()
    # This retrieves the created new_publisher and stores it again (replaces the RETURNING)
    db.refresh(new_perk)  # need orm_mode to be able to be returned

    return req_wrap("perks", new_perk.id)
