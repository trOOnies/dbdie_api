"""Router code for FullModelTypes."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from dbdie_classes.schemas.objects import FullModelTypeOut

from backbone.database import get_db
from backbone.endpoints import (
    delete_one,
    do_count,
    filter_one,
    get_many,
)
from backbone.models.objects import FullModelType

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/count", response_model=int)
def count_fmts(
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count FullModelTypes."""
    return do_count(db, FullModelType, text=text)


@router.get("", response_model=list[FullModelTypeOut])
def get_fmts(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many FullModelTypes."""
    return get_many(db, limit, FullModelType, skip)


@router.get("/{id}", response_model=FullModelTypeOut)
def get_fmt(id: int, db: "Session" = Depends(get_db)):
    """Get a FullModelType with an ID."""
    return filter_one(db, FullModelType, id)[0]


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_fmt(id: int, db: "Session" = Depends(get_db)):
    return delete_one(db, FullModelType, "Full model type", id)
