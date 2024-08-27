from typing import TYPE_CHECKING, Optional

import requests
from backbone.code.characters import create_perks_and_addons, prevalidate_new_character
from backbone.config import endp
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    do_count,
    get_icon,
    get_many,
    get_one,
    get_req,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Addon, Character, Perk
from dbdie_ml.classes.version import DBDVersion
from dbdie_ml.schemas.predictables import (
    CharacterCreate,
    CharacterOut,
    FullCharacterOut,
)
from fastapi import APIRouter, Depends

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_characters(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(Character, text, db)


@router.get("", response_model=list[CharacterOut])
def get_characters(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(Character, limit, skip, db)


@router.get("/{id}", response_model=CharacterOut)
def get_character(id: int, db: "Session" = Depends(get_db)):
    return get_one(Character, "Character", id, db)


@router.get("/{id}/icon")
def get_character_icon(id: int):
    return get_icon("characters", id)


@router.get("/full/{id}", response_model=FullCharacterOut)
def get_full_character(id: int, db: "Session" = Depends(get_db)):
    # TODO: Test out
    character = db.query(Character).filter(Character.id == id).first()
    if character is None:
        raise ItemNotFoundException("Character", id)

    perks = db.query(Perk).filter(Perk.character_id == id).limit(3).all()
    addons = db.query(Addon).filter(Addon.character_id == id).all()

    return {
        "character": character,
        "perks": perks,
        "addons": addons,
    }


@router.post("", response_model=CharacterOut)
def create_character(
    character: CharacterCreate,
    db: "Session" = Depends(get_db),
):
    if NOT_WS_PATT.search(character.name) is None:
        raise ValidationException("Character name can't be empty")

    new_character = {
        "id": requests.get(endp("/characters/count")).json()
    } | character.model_dump()
    new_character = Character(**new_character)

    db.add(new_character)
    db.commit()
    db.refresh(new_character)

    resp = get_req("characters", new_character.id)
    return resp


@router.post("/full", response_model=FullCharacterOut)
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
