import os
from typing import TYPE_CHECKING

import requests
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, endp, get_req
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Character, Status
from constants import ICONS_FOLDER
from dbdie_ml.schemas.predictables import StatusCreate, StatusOut
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=list[StatusOut])
def get_statuses(db: "Session" = Depends(get_db)):
    perks = (
        db.query(
            Status.id,
            Status.name,
            Status.character_id,
            Status.is_dead,
            Character.is_killer.label("is_for_killer"),
        )
        .join(Character)
        .all()
    )
    return perks


@router.get("/{id}", response_model=StatusOut)
def get_status(id: int, db: "Session" = Depends(get_db)):
    status_ = (
        db.query(
            Status.id,
            Status.name,
            Status.character_id,
            Status.is_dead,
            Character.is_killer.label("is_for_killer"),
        )
        .join(Character)
        .filter(Status.id == id)
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


@router.post("", response_model=StatusOut)
def create_status(status: StatusCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(status.name) is None:
        raise ValidationException("Status name can't be empty")

    assert requests.get(endp(f"/characters/{status.character_id}")).status_code == 200

    new_status = {
        "id": requests.get(endp("/statuses/count")).json()
    } | status.model_dump()
    new_status = Status(**new_status)

    db.add(new_status)
    db.commit()
    db.refresh(new_status)

    return get_req("status", new_status.id)
