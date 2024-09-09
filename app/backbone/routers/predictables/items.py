"""Router code for DBD game item."""

from typing import TYPE_CHECKING

import requests
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    do_count,
    endp,
    filter_one,
    get_icon,
    get_many,
    get_req,
)
from backbone.exceptions import ValidationException
from backbone.models import Item
from dbdie_ml.schemas.predictables import ItemCreate, ItemOut
from fastapi import APIRouter, Depends

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_items(
    is_for_killer: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    return do_count(Item, text, db, is_for_killer)


@router.get("", response_model=list[ItemOut])
def get_items(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Item, skip)


@router.get("/{id}", response_model=ItemOut)
def get_item(id: int, db: "Session" = Depends(get_db)):
    return filter_one(Item, "Item", id, db)[0]


@router.get("/{id}/icon")
def get_item_icon(id: int):
    return get_icon("items", id)


@router.post("", response_model=ItemOut)
def create_item(item: ItemCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(item.name) is None:
        raise ValidationException("Item name can't be empty")

    # TODO: assert type_id exists

    new_item = {"id": requests.get(endp("/items/count")).json()} | item.model_dump()
    new_item = Item(**new_item)

    add_commit_refresh(new_item, db)

    return get_req("items", new_item.id)
