"""Router code for DBD characters."""

from typing import TYPE_CHECKING

import requests
from backbone.code.characters import create_addons, create_perks
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    dbd_version_str_to_id,
    endp,
    filter_one,
    filter_with_text,
    get_icon,
    get_req,
    parse_or_raise,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Addon, Character, Perk
from dbdie_ml.schemas.predictables import (
    CharacterCreate,
    CharacterOut,
    FullCharacterCreate,
    FullCharacterOut,
)
from fastapi import APIRouter, Depends

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_characters(
    is_killer: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count DBD characters."""
    cols = []

    if is_killer is not None:
        cols.append(Character.is_killer)
    if text != "":
        cols.append(Character.name)

    if not cols:
        cols = [Character.id]

    query = db.query(*cols)

    if is_killer is not None:
        query = query.filter(Character.is_killer == is_killer)
    if text != "":
        query = filter_with_text(query, Character, text)

    return query.count()


@router.get("", response_model=list[CharacterOut])
def get_characters(
    is_killer: bool | None = None,
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many DBD characters."""
    assert limit > 0

    characters = db.query(Character)
    if is_killer is not None:
        characters = characters.filter(Character.is_killer == is_killer)

    characters = characters.limit(limit)
    if skip == 0:
        return characters.all()
    else:
        return characters.offset(skip).all()


@router.get("/{id}", response_model=CharacterOut)
def get_character(id: int, db: "Session" = Depends(get_db)):
    """Get a DBD character with an ID."""
    return filter_one(Character, "Character", id, db)[0]


@router.get("/{id}/icon")
def get_character_icon(id: int):
    """Get a DBD character icon."""
    return get_icon("characters", id)


@router.get("/full/{id}", response_model=FullCharacterOut)
def get_full_character(id: int, db: "Session" = Depends(get_db)):
    """Get a DBD character with an ID, with his/her full information."""
    # TODO: Test out
    character = db.query(Character).filter(Character.id == id).first()
    if character is None:
        raise ItemNotFoundException("Character", id)

    perks = db.query(Perk).filter(Perk.character_id == id).limit(3).all()
    addons = (
        db.query(Addon).filter(Addon.character_id == id).all()
        if character.is_killer.value
        else []
    )

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
    """Create a DBD character."""
    if NOT_WS_PATT.search(character.name) is None:
        raise ValidationException("Character name can't be empty")

    new_character = {
        "id": requests.get(endp("/characters/count")).json()
    } | character.model_dump()

    if new_character["dbd_version_str"] is not None:
        new_character["dbd_version_id"] = dbd_version_str_to_id(
            new_character["dbd_version_str"]
        )
    del new_character["dbd_version_str"]

    new_character = Character(**new_character)
    add_commit_refresh(new_character, db)

    resp = get_req("characters", new_character.id)
    return resp


@router.post("/full", response_model=FullCharacterOut)
def create_character_full(character: FullCharacterCreate):
    """Create a DBD character in full (with its perks and addons, if applies)."""
    payload = {
        "name": character.name,
        "is_killer": character.is_killer,
        "dbd_version_str": str(character.dbd_version),
        "base_char_id": None,
    }
    character_only = requests.post(endp("/characters"), json=payload)

    character_only = parse_or_raise(character_only)

    perks = create_perks(character_only, character.perk_names)
    addons = create_addons(character_only, character.addon_names)

    return {"character": character_only, "perks": perks, "addons": addons}
