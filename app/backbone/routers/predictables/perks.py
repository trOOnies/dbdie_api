"""Router code for DBD perks."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.predictables import PerkCreate, PerkOut
from fastapi import APIRouter, Depends, status
from sqlalchemy import or_

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    delete_one,
    do_count,
    get_icon,
    get_many,
    get_req,
    getr,
    update_one,
    update_many,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models.groupings import Labels
from backbone.models.predictables import Character, Perk
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_perks(
    ifk: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count DBD perks."""
    return do_count(db, Perk, text=text, ifk=ifk)


@router.get("", response_model=list[PerkOut])
def get_perks(
    limit: int = 10,
    skip: int = 0,
    ifk: bool | None = None,
    db: "Session" = Depends(get_db),
):
    """Get many DBD perks."""
    return get_many(db, limit, Perk, skip, ifk, Character)


@router.get("/{id}", response_model=PerkOut)
def get_perk(id: int, db: "Session" = Depends(get_db)):
    """Get a specific DBD perk with an ID."""
    perk = (
        db.query(
            Perk.id,
            Perk.name,
            Perk.character_id,
            Perk.dbdv_id,
            Perk.emoji,
            Character.ifk,
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
    """Get a DBD perk icon."""
    return get_icon("perks", id)


@router.post("", response_model=PerkOut, status_code=status.HTTP_201_CREATED)
def create_perk(perk: PerkCreate, db: "Session" = Depends(get_db)):
    """Create a DBD perk."""
    if NOT_WS_PATT.search(perk.name) is None:
        raise ValidationException("Perk name can't be empty")

    getr(f"{EP.CHARACTER}/{perk.character_id}")

    new_perk = {"id": getr(f"{EP.PERKS}/count")} | perk.model_dump()
    new_perk = Perk(**new_perk)

    add_commit_refresh(db, new_perk)

    return get_req(EP.PERKS, new_perk.id)


@router.put("/{id}/change_id", response_model=PerkOut)
def change_perk_id(
    id: int,
    new_id: int,
    db: "Session" = Depends(get_db),
):
    assert new_id >= 0, "The new ID cannot be negative."
    perk = getr(f"{EP.PERKS}/{id}")

    # Check that the new perk id isn't taken
    try:
        getr(f"{EP.PERKS}/{new_id}")
    except Exception:
        pass
    else:
        raise AssertionError(f"New id '{new_id}' already exists.")

    resp = update_one(db, perk, Perk, "Perk", id, new_id=new_id)
    assert resp.status_code == status.HTTP_200_OK

    def update_cols(record) -> None:
        for col_name in ["perks_0", "perks_1", "perks_2", "perks_3"]:
            if getattr(record, col_name) == id:
                setattr(record, col_name, new_id)

    update_many(
        db,
        Labels,
        filter=or_(
            Labels.perks_0 == id,
            Labels.perks_1 == id,
            Labels.perks_2 == id,
            Labels.perks_3 == id,
        ),
        update_f=update_cols,
    )

    # TODO: Deprecate perk models and extractors that use them
    # ...

    perk.id = new_id
    return perk


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_perk(id: int, perk: PerkCreate, db: "Session" = Depends(get_db)):
    """Update the information of a DBD perk."""
    return update_one(db, perk, Perk, "Perk", id)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_perk(id: int, db: "Session" = Depends(get_db)):
    return delete_one(db, Perk, "Perk", id)
