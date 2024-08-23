import os
from dbdie_ml.schemas.predictables import Status
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import FileResponse

from constants import ICONS_FOLDER
from backbone import models
from backbone.database import get_db
from backbone.exceptions import ItemNotFoundException

router = APIRouter()


@router.get("", response_model=list[Status])
def get_statuses(db: "Session" = Depends(get_db)):
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


@router.get("/{id}", response_model=Status)
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
        raise ItemNotFoundException("Status", id)
    return status_


@router.get("/{id}/image")
def get_status_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"status/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Status image", id)
    return FileResponse(path)
