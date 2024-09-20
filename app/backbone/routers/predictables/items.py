"""Router code for DBD game item."""

import requests
from typing import TYPE_CHECKING
from dbdie_ml.schemas.predictables import ItemCreate, ItemOut, ItemTypeOut
from fastapi import APIRouter, Depends

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
    get_types,
)
from backbone.exceptions import ValidationException
from backbone.models import Item, ItemType
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_items(
    is_for_killer: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    return do_count(Item, text, db, is_for_killer, ItemType)


@router.get("", response_model=list[ItemOut])
def get_items(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Item, skip)


@router.get("/types", response_model=list[ItemTypeOut])
def get_item_types(db: "Session" = Depends(get_db)):
    return get_types(db, ItemType)


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

    new_item = {"id": requests.get(endp(f"{EP.ITEM}/count")).json()} | item.model_dump()
    new_item = Item(**new_item)

    add_commit_refresh(new_item, db)

    return get_req(EP.ITEM, new_item.id)
