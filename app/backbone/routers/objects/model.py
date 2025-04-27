"""Router code for DBDIE IEModel."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.objects import ModelCreate, ModelOut
from fastapi import APIRouter, Depends, status
from requests import delete as req_delete

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    delete_one,
    do_count,
    filter_one,
    get_id,
    get_many,
    get_req,
    mlendp,
    update_with_creation_schema,
)
from backbone.exceptions import ValidationException
from backbone.models.objects import Model
from backbone.options import ENDPOINT as EP
from backbone.options import ML_ENDPOINT as MLEP

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


@router.get("/id", response_model=int)
def get_model_id(
    model_name: str,
    db: "Session" = Depends(get_db),
):
    """Get Model id from its name."""
    return get_id(db, Model, model_name)


@router.get("/{id}", response_model=ModelOut)
def get_model(id: int, db: "Session" = Depends(get_db)):
    """Get a Model with an ID."""
    return filter_one(db, Model, id)[0]


@router.post("/{id}", response_model=ModelOut, status_code=status.HTTP_201_CREATED)
def create_model(
    id: int,
    model: ModelCreate,
    db: "Session" = Depends(get_db),
):
    """Create a DBD character."""
    if NOT_WS_PATT.search(model.name) is None:
        raise ValidationException("Model name can't be empty.")

    new_model = model.model_dump() | {"id": id}

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
    return update_with_creation_schema(db, Model, id, model)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_model(id: int, db: "Session" = Depends(get_db)):
    req_delete(mlendp(f"{MLEP.DELETE}/model/{id}"))
    return delete_one(db, Model, id)
