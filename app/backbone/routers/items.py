from typing import TYPE_CHECKING

import requests
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    do_count,
    endp,
    get_icon,
    get_many,
    get_one,
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
def count_items(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(Item, text, db)


@router.get("", response_model=list[ItemOut])
def get_items(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(Item, limit, skip, db)


@router.get("/{id}", response_model=ItemOut)
def get_item(id: int, db: "Session" = Depends(get_db)):
    return get_one(Item, "Item", id, db)


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

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return get_req("items", new_item.id)
