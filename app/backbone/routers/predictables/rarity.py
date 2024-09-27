"""Router for item ratity."""

from dbdie_classes.schemas.types import RarityOut
from fastapi import APIRouter, Depends
from typing import TYPE_CHECKING

from backbone.database import get_db
from backbone.endpoints import (
    do_count,
    filter_one,
    get_many,
)
from backbone.models.types import Rarity

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_items(
    ifk: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    return do_count(db, Rarity, text=text, ifk=ifk)


@router.get("", response_model=list[RarityOut])
def get_items(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Rarity, skip)


@router.get("/{id}", response_model=RarityOut)
def get_item(id: int, db: "Session" = Depends(get_db)):
    return filter_one(db, Rarity, "Rarity", id)[0]
