"""Router code for DBD offerings."""

from typing import TYPE_CHECKING

import requests
from dbdie_ml.schemas.predictables import OfferingCreate, OfferingOut, OfferingTypeOut
from fastapi import APIRouter, Depends

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    do_count,
    endp,
    get_icon,
    get_req,
    get_types,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Character, Offering, OfferingType
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_offerings(
    is_for_killer: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count DBD offerings."""
    return do_count(Offering, text, db, is_for_killer, OfferingType)


@router.get("", response_model=list[OfferingOut])
def get_offerings(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Get many DBD offerings."""
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


@router.get("/types", response_model=list[OfferingTypeOut])
def get_offering_types(db: "Session" = Depends(get_db)):
    return get_types(db, OfferingType)


@router.get("/{id}", response_model=OfferingOut)
def get_offering(id: int, db: "Session" = Depends(get_db)):
    """Get a DBD offering with a certain ID."""
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


@router.get("/{id}/icon")
def get_offering_icon(id: int):
    """Get a DBD offering icon."""
    return get_icon("offerings", id)


@router.post("", response_model=OfferingOut)
def create_offering(offering: OfferingCreate, db: "Session" = Depends(get_db)):
    """Create a DBD offering."""
    if NOT_WS_PATT.search(offering.name) is None:
        raise ValidationException("Offering name can't be empty")

    # TODO: assert type_id and user_id exists

    new_offering = {
        "id": requests.get(endp(f"{EP.OFFERING}/count")).json()
    } | offering.model_dump()
    new_offering = Offering(**new_offering)

    add_commit_refresh(new_offering, db)

    return get_req(EP.OFFERING, new_offering.id)
