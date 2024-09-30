"""Router code for DBD game item."""

from typing import TYPE_CHECKING
from dbdie_classes.schemas.predictables import ItemCreate, ItemOut
from dbdie_classes.schemas.types import ItemTypeOut
from fastapi import APIRouter, Depends

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    do_count,
    filter_one,
    get_icon,
    get_many,
    get_req,
    get_types,
    poke,
)
from backbone.exceptions import ValidationException
from backbone.models.predictables import Item, ItemType
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_items(
    ifk: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    return do_count(db, Item, text=text, ifk=ifk, model_type=ItemType)


@router.get("", response_model=list[ItemOut])
def get_items(
    limit: int = 10,
    skip: int = 0,
    ifk: bool | None = None,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Item, skip, ifk, ItemType)


@router.get("/types", response_model=list[ItemTypeOut])
def get_item_types(db: "Session" = Depends(get_db)):
    return get_types(db, ItemType)


@router.get("/{id}", response_model=ItemOut)
def get_item(id: int, db: "Session" = Depends(get_db)):
    return filter_one(db, Item, id)[0]


@router.get("/{id}/icon")
def get_item_icon(id: int):
    return get_icon("items", id)


@router.post("", response_model=ItemOut)
def create_item(item: ItemCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(item.name) is None:
        raise ValidationException("Item name can't be empty")

    # TODO: assert type_id exists

    new_item = {"id": poke(f"{EP.ITEM}/count")} | item.model_dump()
    new_item = Item(**new_item)

    add_commit_refresh(db, new_item)

    return get_req(EP.ITEM, new_item.id)
