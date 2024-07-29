import os
from dbdie_ml import schemas
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from constants import ICONS_FOLDER
from backbone import models
from backbone.database import get_db

router = APIRouter()


@router.get("", response_model=list[schemas.Offering])
def get_offerings(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    offerings = (
        db.query(
            models.Offering.id,
            models.Offering.name,
            models.Offering.type_id,
            models.Offering.user_id,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .limit(limit)
        .offset(skip)
        .all()
    )
    return offerings


@router.get("/{id}", response_model=schemas.Offering)
def get_offering(id: int, db: "Session" = Depends(get_db)):
    offering = (
        db.query(
            models.Offering.id,
            models.Offering.name,
            models.Offering.type_id,
            models.Offering.user_id,
            models.Character.is_killer.label("is_for_killer"),
        )
        .join(models.Character)
        .filter(models.Offering.id == id)
        .first()
    )
    if offering is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"offering with id {id} was not found",
        )
    return offering


@router.get("/{id}/image")
def get_offering_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"offerings/{id}.png")
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"offering image with id {id} was not found",
        )
    return FileResponse(path)
