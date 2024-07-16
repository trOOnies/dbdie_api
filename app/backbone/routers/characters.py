import os
import requests
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from dbdie_ml import schemas
from constants import ICONS_FOLDER
from backbone import models
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, filter_with_text, req_wrap
from backbone.code.characters import prevalidate_new_character, create_perks_and_addons

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/count", response_model=int)
def count_characters(
    text: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(models.Character)
    if text != "":
        query = filter_with_text(query, text, use_model="character")
    return query.count()


@router.get("", response_model=list[schemas.Character])
def get_characters(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db)
):
    characters = (
        db.query(models.Character)
        .limit(limit)
        .offset(skip)
        .all()
    )
    return characters


@router.get("/{id}", response_model=schemas.Character)
def get_character(id: int, db: "Session" = Depends(get_db)):
    character = (
        db.query(models.Character)
        .filter(models.Character.id == id)
        .first()
    )
    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"character with id {id} was not found",
        )
    return character


@router.get("/{id}/image")
def get_character_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"characters/{id}.png")
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"character image with id {id} was not found",
        )
    return FileResponse(path)


@router.post("", response_model=schemas.Character)
def create_character(
    character: schemas.CharacterCreate,
    db: "Session" = Depends(get_db)
):
    if NOT_WS_PATT.search(character.name) is None:
        return status.HTTP_400_BAD_REQUEST

    new_character = character.model_dump()
    new_character["id"] = requests.get(f"{os.environ['HOST']}/characters/count").json()
    new_character = models.Character(**new_character)

    db.add(new_character)
    db.commit()
    # This retrieves the created new_publisher and stores it again (replaces the RETURNING)
    db.refresh(new_character)  # need orm_mode to be able to be returned

    resp = req_wrap("characters", new_character.id)
    return resp


@router.post("/full", response_model=schemas.FullCharacter)
def create_character_full(
    name: str,
    is_killer: bool,
    perk_names: list[str],
    addon_names: Optional[list[str]] = None
):
    prevalidate_new_character(perk_names, addon_names, is_killer)

    character = requests.post(
        f"{os.environ['HOST']}/characters",
        json={"name": name, "is_killer": is_killer}
    )
    character = character.json()

    perks, addons = create_perks_and_addons(
        character,
        perk_names,
        addon_names
    )

    return {
        "character": character,
        "perks": perks,
        "addons": addons
    }
