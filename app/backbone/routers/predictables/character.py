"""Router code for DBD characters."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.groupings import (
    FullCharacterCreate,
    FullCharacterOut,
)
from dbdie_classes.schemas.predictables import (
    CharacterCreate,
    CharacterOut,
)
from fastapi import APIRouter, Depends
import requests

from backbone.code.characters import (
    create_addons,
    create_killer_power,
    create_perks,
)
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    dbd_version_str_to_id,
    do_count,
    endp,
    filter_one,
    get_icon,
    get_many,
    get_req,
    parse_or_raise,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models.predictables import Addon, Character, Item, Perk
from backbone.options import ENDPOINTS as EP

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
    return do_count(db, Character, is_killer, text=text)


@router.get("", response_model=list[CharacterOut])
def get_characters(
    is_killer: bool | None = None,
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many DBD characters."""
    return get_many(db, limit, Character, skip, is_killer)


@router.get("/{id}", response_model=CharacterOut)
def get_character(id: int, db: "Session" = Depends(get_db)):
    """Get a DBD character with an ID."""
    return filter_one(db, Character, "Character", id)[0]


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

    return {
        "character": character,
        "power": (
            db.query(Item).filter(Item.character_id).first()
            if character.is_killer.value
            else None
        ),
        "perks": db.query(Perk).filter(Perk.character_id == id).limit(3).all(),
        "addons": (
            db.query(Addon).filter(Addon.character_id == id).all()
            if character.is_killer.value
            else None
        ),
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
        "id": requests.get(endp(f"{EP.CHARACTER}/count")).json()
    } | character.model_dump()

    if new_character["dbd_version_str"] is not None:
        new_character["dbd_version_id"] = dbd_version_str_to_id(
            new_character["dbd_version_str"]
        )
    del new_character["dbd_version_str"]

    new_character = Character(**new_character)
    add_commit_refresh(db, new_character)

    resp = get_req(EP.CHARACTER, new_character.id)
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
    character_only = parse_or_raise(
        requests.post(endp(EP.CHARACTER), json=payload)
    )

    return {
        "character": character_only,
        "power": create_killer_power(character.power_name),
        "perks": create_perks(character_only, character.perk_names),
        "addons": create_addons(character_only, character.addon_names),
    }
