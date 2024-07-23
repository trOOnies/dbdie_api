import os
from dbdie_ml import schemas
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from constants import ICONS_FOLDER
from backbone import models
from backbone.database import get_db

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[schemas.Item])
def get_items(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    items = db.query(models.Item).limit(limit).offset(skip).all()
    return items


@router.get("/{id}", response_model=schemas.Item)
def get_item(id: int, db: "Session" = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"item with id {id} was not found",
        )
    return item


@router.get("/{id}/image")
def get_item_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"items/{id}.png")
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"item image with id {id} was not found",
        )
    return FileResponse(path)
