import os
import requests
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, status
from fastapi.responses import FileResponse
from dbdie_ml.schemas.predictables import Character, CharacterCreate, FullCharacter
from dbdie_ml.classes.version import DBDVersion

from constants import ICONS_FOLDER
from backbone import models
from backbone.config import endp
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, filter_with_text, req_wrap
from backbone.exceptions import ItemNotFoundException
from backbone.code.characters import prevalidate_new_character, create_perks_and_addons

router = APIRouter()


@router.get("/count", response_model=int)
def count_characters(text: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Character)
    if text != "":
        query = filter_with_text(query, text, use_model="character")
    return query.count()


@router.get("", response_model=list[Character])
def get_characters(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    characters = db.query(models.Character).limit(limit).offset(skip).all()
    return characters


@router.get("/{id}", response_model=Character)
def get_character(id: int, db: "Session" = Depends(get_db)):
    character = db.query(models.Character).filter(models.Character.id == id).first()
    if character is None:
        raise ItemNotFoundException("Character", id)
    return character


@router.get("/full/{id}", response_model=FullCharacter)
def get_full_character(id: int, db: "Session" = Depends(get_db)):
    # TODO: Test out
    character = db.query(models.Character).filter(models.Character.id == id).first()
    if character is None:
        raise ItemNotFoundException("Character", id)

    perks = db.query(models.Perk).filter(models.Perk.character_id == id).limit(3).all()
    addons = db.query(models.Addon).filter(models.Addon.character_id == id).all()

    return {
        "character": character,
        "perks": perks,
        "addons": addons,
    }


@router.get("/{id}/image")
def get_character_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"characters/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Character image", id)
    return FileResponse(path)


@router.post("", response_model=Character)
def create_character(
    character: CharacterCreate,
    db: "Session" = Depends(get_db),
):
    if NOT_WS_PATT.search(character.name) is None:
        return status.HTTP_400_BAD_REQUEST

    new_character = character.model_dump()
    new_character = {"id": requests.get(endp("/characters/count")).json()} | new_character
    new_character = models.Character(**new_character)

    db.add(new_character)
    db.commit()
    db.refresh(new_character)

    resp = req_wrap("characters", new_character.id)
    return resp


@router.post("/full", response_model=FullCharacter)
def create_character_full(
    name: str,
    is_killer: bool,
    perk_names: list[str],
    dbd_version: DBDVersion,
    addon_names: Optional[list[str]] = None,
):
    prevalidate_new_character(perk_names, addon_names, is_killer)

    dbd_version_id = requests.get(
        endp("/dbd-version"),
        params=dict(dbd_version),
    )

    payload = {"name": name, "is_killer": is_killer, "dbd_version_id": dbd_version_id}
    character = requests.post(endp("/characters"), json=payload)
    character = character.json()

    perks, addons = create_perks_and_addons(character, perk_names, addon_names)

    return {"character": character, "perks": perks, "addons": addons}
