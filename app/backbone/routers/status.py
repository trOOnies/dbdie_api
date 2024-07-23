import os
from dbdie_ml import schemas
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from constants import ICONS_FOLDER
from backbone import models
from backbone.database import get_db

router = APIRouter(prefix="/status", tags=["status"])


@router.get("", response_model=list[schemas.Status])
def get_status(db: "Session" = Depends(get_db)):
    perks = (
        db.query(
            models.Status.id,
            models.Status.name,
            models.Status.character_id,
            models.Status.is_dead,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .all()
    )
    return perks


@router.get("/{id}", response_model=schemas.Status)
def get_status(id: int, db: "Session" = Depends(get_db)):
    status_ = (
        db.query(
            models.Status.id,
            models.Status.name,
            models.Status.character_id,
            models.Status.is_dead,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .filter(models.Status.id == id)
        .first()
    )
    if status_ is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"status with id {id} was not found",
        )
    return status_


@router.get("/{id}/image")
def get_status_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"status/{id}.png")
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"status image with id {id} was not found",
        )
    return FileResponse(path)
