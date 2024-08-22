import os
from dbdie_ml import schemas
from fastapi import Depends, APIRouter
from fastapi.responses import FileResponse
from typing import TYPE_CHECKING

from constants import ICONS_FOLDER
from backbone import models
from backbone.database import get_db
from backbone.exceptions import ItemNotFoundException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=list[schemas.Item])
def get_items(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    items = db.query(models.Item).limit(limit).offset(skip).all()
    return items


@router.get("/{id}", response_model=schemas.Item)
def get_item(id: int, db: "Session" = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if item is None:
        raise ItemNotFoundException("Item", id)
    return item


@router.get("/{id}/image")
def get_item_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"items/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Item image", id)
    return FileResponse(path)
