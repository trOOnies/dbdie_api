"""Router code for DBDIE IEModel."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.objects import ModelCreate, ModelOut
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
from backbone.models.objects import Model
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_models(
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count Models."""
    return do_count(db, Model, text=text)


@router.get("", response_model=list[ModelOut])
def get_models(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many Models."""
    return get_many(db, limit, Model, skip)


@router.get("/{id}", response_model=ModelOut)
def get_model(id: int, db: "Session" = Depends(get_db)):
    """Get a Model with an ID."""
    return filter_one(db, Model, id)[0]


@router.post("/{id}", response_model=ModelOut)
def create_model(
    id: int,
    model: ModelCreate,
    db: "Session" = Depends(get_db),
):
    """Create a DBD character."""
    if NOT_WS_PATT.search(model.name) is None:
        raise ValidationException("Model name can't be empty.")

    new_model = {"id": id} | model.model_dump()

    new_model = Model(**new_model)
    add_commit_refresh(db, new_model)

    resp = get_req(EP.MODELS, new_model.id)
    return resp


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_model(
    id: int,
    model: ModelCreate,
    db: "Session" = Depends(get_db),
):
    """Update the information of an IEModel in the database."""
    # TODO: Update its config as well, and only allow sensible modifications.
    return update_one(db, model, Model, "Model", id)
