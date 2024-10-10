"""Router code for DBD offerings."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.predictables import OfferingCreate, OfferingOut
from dbdie_classes.schemas.types import OfferingTypeOut
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
    getr,
)
from backbone.exceptions import ValidationException
from backbone.models.predictables import Character, Offering, OfferingType
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_offerings(
    ifk: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count DBD offerings."""
    return do_count(db, Offering, text=text, ifk=ifk, model_type=OfferingType)


@router.get("", response_model=list[OfferingOut])
def get_offerings(
    limit: int = 10,
    skip: int = 0,
    ifk: bool | None = None,
    db: "Session" = Depends(get_db),
):
    """Get many DBD offerings."""
    return get_many(db, limit, Offering, skip, ifk, Character)


@router.get("/types", response_model=list[OfferingTypeOut])
def get_offering_types(db: "Session" = Depends(get_db)):
    return get_types(db, OfferingType)


@router.get("/{id}", response_model=OfferingOut)
def get_offering(id: int, db: "Session" = Depends(get_db)):
    """Get a DBD offering with a certain ID."""
    return filter_one(db, Offering, id)[0]


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

    new_offering = {"id": getr(f"{EP.OFFERING}/count")} | offering.model_dump()
    new_offering = Offering(**new_offering)

    add_commit_refresh(db, new_offering)

    return get_req(EP.OFFERING, new_offering.id)
