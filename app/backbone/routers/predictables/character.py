"""Router code for DBD characters."""

from typing import TYPE_CHECKING

from dbdie_classes.options.MODEL_TYPE import CHARACTER
from dbdie_classes.options.NULL_IDS import INT_IDS as NULL_INT_IDS
from dbdie_classes.schemas.groupings import (
    FullCharacterCreate,
    FullCharacterOut,
)
from dbdie_classes.schemas.predictables import (
    CharacterCreate,
    CharacterOut,
)
from fastapi import APIRouter, Depends, status
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
    dbdv_str_to_id,
    delete_one,
    do_count,
    endp,
    filter_one,
    get_icon,
    get_many,
    get_req,
    postr,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models.predictables import Addon, Character, Item, Perk
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_characters(
    ifk: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count DBD characters."""
    return do_count(db, Character, ifk, text=text)


@router.get("", response_model=list[CharacterOut])
def get_characters(
    ifk: bool | None = None,
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many DBD characters."""
    return get_many(db, limit, Character, skip, ifk)


@router.get("/{id}", response_model=CharacterOut)
def get_character(id: int, db: "Session" = Depends(get_db)):
    """Get a DBD character with an ID."""
    return filter_one(db, Character, id)[0]


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

    is_null_id = id in NULL_INT_IDS[CHARACTER]
    is_killer = (character.ifk is not None) and character.ifk

    power = (
        db.query(Item).filter(Item.id == character.power_id).first()
        if (not is_null_id) and is_killer else None
    )

    return {
        "character": character,
        "power": power,
        "perks": (
            db.query(Perk).filter(Perk.character_id == id).limit(3).all()
            if not is_null_id else None
        ),
        "addons": (
            db.query(Addon).filter(Addon.item_id == power.id).limit(20).all()
            if power is not None else None
        ),
    }



@router.post("", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(
    character: CharacterCreate,
    db: "Session" = Depends(get_db),
):
    """Create a DBD character."""
    if NOT_WS_PATT.search(character.name) is None:
        raise ValidationException("Character name can't be empty")

    new_character = {
        "id": requests.get(endp(f"{EP.CHARACTER}/count"))
    } | character.model_dump()

    if new_character["dbdv_str"] is not None:
        new_character["dbdv_id"] = dbdv_str_to_id(
            new_character["dbdv_str"]
        )
    del new_character["dbdv_str"]

    new_character = Character(**new_character)
    add_commit_refresh(db, new_character)

    resp = get_req(EP.CHARACTER, new_character.id)
    return resp


@router.post("/full", response_model=FullCharacterOut, status_code=status.HTTP_201_CREATED)
def create_character_full(character: FullCharacterCreate):
    """Create a DBD character in full (with its perks and addons, if applies)."""
    payload = {
        "name": character.name,
        "ifk": character.ifk,
        "dbdv_str": str(character.dbdv),
        "base_char_id": None,
    }
    character_only = postr(EP.CHARACTER, json=payload)

    return {
        "character": character_only,
        "power": create_killer_power(character.power_name),
        "perks": create_perks(character_only, character.perk_names),
        "addons": create_addons(character_only, character.addon_names),
    }


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_character(id: int, db: "Session" = Depends(get_db)):
    return delete_one(db, Character, "Character", id)
