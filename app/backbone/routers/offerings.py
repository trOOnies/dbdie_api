import os
from typing import TYPE_CHECKING

import requests
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, endp, get_req
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Character, Offering
from constants import ICONS_FOLDER
from dbdie_ml.schemas.predictables import OfferingCreate, OfferingOut
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=list[OfferingOut])
def get_offerings(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    offerings = (
        db.query(
            Offering.id,
            Offering.name,
            Offering.type_id,
            Offering.user_id,
            Character.is_killer.label("is_for_killer"),
        )
        .join(Character)
        .limit(limit)
        .offset(skip)
        .all()
    )
    return offerings


@router.get("/{id}", response_model=OfferingOut)
def get_offering(id: int, db: "Session" = Depends(get_db)):
    offering = (
        db.query(
            Offering.id,
            Offering.name,
            Offering.type_id,
            Offering.user_id,
            Character.is_killer.label("is_for_killer"),
        )
        .join(Character)
        .filter(Offering.id == id)
        .first()
    )
    if offering is None:
        raise ItemNotFoundException("Offering", id)
    return offering


@router.get("/{id}/image")
def get_offering_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"offerings/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Offering image", id)
    return FileResponse(path)


@router.post("", response_model=OfferingOut)
def create_offering(offering: OfferingCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(offering.name) is None:
        raise ValidationException("Offering name can't be empty")

    # TODO: assert type_id and user_id exists

    new_offering = {
        "id": requests.get(endp("/offerings/count")).json()
    } | offering.model_dump()
    new_offering = Offering(**new_offering)

    db.add(new_offering)
    db.commit()
    db.refresh(new_offering)

    return get_req("offerings", new_offering.id)
