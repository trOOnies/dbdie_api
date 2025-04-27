"""Router code for DBDIE InfoExtractor."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.objects import ExtractorCreate, ExtractorOut
from fastapi import APIRouter, Depends, Response, status
from requests import delete as req_delete

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    delete_one,
    do_count,
    endp,
    filter_one,
    get_id,
    get_many,
    get_req,
    mlendp,
    update_many,
    update_with_creation_schema,
)
from backbone.exceptions import ValidationException
from backbone.models.groupings import Labels
from backbone.models.objects import Extractor
from backbone.options import ENDPOINT as EP
from backbone.options import ML_ENDPOINT as MLEP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=list[ExtractorOut])
def get_extractors(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many Extractors."""
    extractors = get_many(db, limit, Extractor, skip)
    return [ExtractorOut.from_sqla(ext) for ext in extractors]


@router.get("/count", response_model=int)
def count_extractors(
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count Extractors."""
    return do_count(db, Extractor, text=text)


@router.get("/id", response_model=int)
def get_extractor_id(
    extr_name: str,
    db: "Session" = Depends(get_db),
):
    """Get Extractor id from its name."""
    return get_id(db, Extractor, extr_name)


@router.get("/{id}", response_model=ExtractorOut)
def get_extractor(id: int, db: "Session" = Depends(get_db)):
    """Get a Extractor with an ID."""
    extractor = filter_one(db, Extractor, id)[0]
    return ExtractorOut.from_sqla(extractor)


@router.post("/{id}", response_model=ExtractorOut, status_code=status.HTTP_201_CREATED)
def create_extractor(
    id: int,
    extractor: ExtractorCreate,
    db: "Session" = Depends(get_db),
):
    """Register an InfoExtractor."""
    if NOT_WS_PATT.search(extractor.name) is None:
        raise ValidationException("Extractor name can't be empty.")

    new_extractor = extractor.model_dump() | {"id": id}
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
    return update_with_creation_schema(db, Extractor, id, extractor)


def update_labels_f(record) -> None:
    setattr(record, "extr_id", None)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_extractor(
    id: int,
    delete_models: bool = False,
    db: "Session" = Depends(get_db),
):
    # Nullify extr_id in labels that used it for extraction
    update_many(
        db,
        Labels,
        filter=(Labels.extr_id == id),
        update_f=update_labels_f,
    )

    if delete_models:
        extr = get_req(EP.EXTRACTOR, id)

    # Delete extractor
    resp_extr = req_delete(mlendp(f"{MLEP.DELETE}/extractor/{id}"))
    assert resp_extr.status_code == status.HTTP_200_OK, resp_extr.text
    resp_extr = delete_one(db, Extractor, id)
    assert resp_extr.status_code == status.HTTP_200_OK, resp_extr.text

    # Delete models using this API (if requested)
    if delete_models:
        models_ids = [mid for mid in extr["models_ids"].values() if mid is not None]
        for mid in models_ids:
            resp_model = req_delete(endp(f"{EP.MODELS}/{mid}"))
            assert resp_model.status_code == status.HTTP_200_OK, resp_model.text

    return Response(status_code=status.HTTP_200_OK)
