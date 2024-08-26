import os
from typing import TYPE_CHECKING

import requests
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, endp, get_req
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Item
from constants import ICONS_FOLDER
from dbdie_ml.schemas.predictables import ItemCreate, ItemOut
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=list[ItemOut])
def get_items(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    items = db.query(Item).limit(limit).offset(skip).all()
    return items


@router.get("/{id}", response_model=ItemOut)
def get_item(id: int, db: "Session" = Depends(get_db)):
    item = db.query(Item).filter(Item.id == id).first()
    if item is None:
        raise ItemNotFoundException("Item", id)
    return item


@router.get("/{id}/image")
def get_item_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"items/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Item image", id)
    return FileResponse(path)


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
