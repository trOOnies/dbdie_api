"""Router for item ratity."""

from dbdie_classes.schemas.types import RarityCreate, RarityOut
from fastapi import APIRouter, Depends, status
from typing import TYPE_CHECKING

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    delete_one,
    do_count,
    filter_one,
    get_many,
    get_req,
    getr,
)
from backbone.exceptions import ValidationException
from backbone.models.types import Rarity
from backbone.options import ENDPOINT as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=list[RarityOut])
def get_items(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Rarity, skip)


@router.get("/count", response_model=int)
def count_items(
    ifk: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    return do_count(db, Rarity, text=text, ifk=ifk)


@router.get("/{id}", response_model=RarityOut)
def get_item(id: int, db: "Session" = Depends(get_db)):
    return filter_one(db, Rarity, id)[0]


@router.post("", response_model=RarityOut, status_code=status.HTTP_201_CREATED)
def create_rarity(rarity: RarityCreate, db: "Session" = Depends(get_db)):
    """Create a DBD rarity tier."""
    if NOT_WS_PATT.search(rarity.name) is None:
        raise ValidationException("Rarity name can't be empty")

    new_rarity = rarity.model_dump() | {"id": getr(f"{EP.RARITY}/count")}
    new_rarity = Rarity(**new_rarity)

    add_commit_refresh(db, new_rarity)

    return get_req(EP.RARITY, new_rarity.id)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_rarity(id: int, db: "Session" = Depends(get_db)):
    return delete_one(db, Rarity, id)
