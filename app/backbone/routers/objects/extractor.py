"""Router code for DBDIE InfoExtractor."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.objects import ExtractorCreate, ExtractorOut
from fastapi import APIRouter, Depends, status

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    do_count,
    filter_one,
    get_many,
    get_req,
    update_one,
)
from backbone.exceptions import ValidationException
from backbone.models.objects import Extractor
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/count", response_model=int)
def count_extractors(
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count Extractors."""
    return do_count(db, Extractor, text=text)


@router.get("", response_model=list[ExtractorOut])
def get_extractors(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many Extractors."""
    extractors = get_many(db, limit, Extractor, skip)
    return [
        ExtractorOut.from_sqla(ext)
        for ext in extractors
    ]


@router.get("/{id}", response_model=ExtractorOut)
def get_extractor(id: int, db: "Session" = Depends(get_db)):
    """Get a Extractor with an ID."""
    extractor = filter_one(db, Extractor, id)[0]
    return ExtractorOut.from_sqla(extractor)


@router.post("/{id}", response_model=ExtractorOut)
def create_extractor(
    id: int,
    extractor: ExtractorCreate,
    db: "Session" = Depends(get_db),
):
    """Create a DBD character."""
    if NOT_WS_PATT.search(extractor.name) is None:
        raise ValidationException("Extractor name can't be empty.")

    new_extractor = {"id": id} | extractor.model_dump()
    del new_extractor["models_ids"]
    new_extractor = new_extractor | extractor.models_ids.to_sql_cols()

    new_extractor = Extractor(**new_extractor)
    add_commit_refresh(db, new_extractor)

    resp = get_req(EP.EXTRACTOR, new_extractor.id)
    return resp


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_extractor(
    id: int,
    extractor: ExtractorCreate,
    db: "Session" = Depends(get_db),
):
    """Update the information of an InfoExtractor in the database."""
    # TODO: Update its config as well, and only allow sensible modifications.
    return update_one(db, extractor, Extractor, "Extractor", id)
