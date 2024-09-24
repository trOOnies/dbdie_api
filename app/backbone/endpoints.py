"""Endpoints-related helper functions."""

import os
import re
from typing import TYPE_CHECKING

import requests
from fastapi import Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

from backbone.config import ST
from backbone.exceptions import ItemNotFoundException, NameNotFoundException
from backbone.options import ENDPOINTS as EP
from backbone.options import TABLE_NAMES as TN
from backbone.sqla import fill_cols, filter_with_text
from constants import ICONS_FOLDER

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


ENDPOINT_PATT = re.compile(r"\/[a-z\-]+$")
NOT_WS_PATT = re.compile(r"\S")


def endp(endpoint: str) -> str:
    """Get full URL of the endpoint."""
    return ST.fastapi_host + endpoint


def get_req(endpoint: str, id: int) -> dict:
    """Request wrapper for a GET request for a type 'endpoint' with an id 'id'."""
    assert ENDPOINT_PATT.match(endpoint)
    resp = requests.get(endp(f"{endpoint}/{id}"))
    if resp.status_code != status.HTTP_200_OK:
        raise ItemNotFoundException(endpoint[1:].capitalize()[:-1], id)
    return resp.json()


def parse_or_raise(resp, exp_status_code: int = status.HTTP_200_OK):
    """Parse Response as JSON or raise error as exception, depending on status code."""
    if resp.status_code != exp_status_code:
        raise HTTPException(
            status_code=resp.status_code,
            detail=resp.reason,
        )
    return resp.json()


# * Base endpoint functions


def do_count(
    db: "Session",
    model,
    text: str,
    is_for_killer: bool | None = None,
    type_model = None,
) -> int:
    """Base count function.
    'model' is the sqlalchemy model.
    """
    filled = {
        "text": text != "",
        "is_for_killer": is_for_killer is not None,
        "type_model": type_model is not None,
    }

    # If no filter was applied, just do a count
    if not any(filled.values()):
        return db.query(model.id).count()

    # Base query
    cols = fill_cols(model, text, is_for_killer, type_model)
    query = db.query(*cols)
    if filled["type_model"]:
        query = query.join(type_model)

    # Other filters
    if filled["is_for_killer"]:
        if type_model is not None:
            query = query.filter(type_model.is_for_killer == is_for_killer)
        else:
            query = query.filter(model.is_for_killer == is_for_killer)
    if filled["text"]:
        query = filter_with_text(query, model, text)

    return query.count()


def filter_one(db: "Session", model, model_str: str, id: int):
    """Base get one (item) function.

    'model' is the sqlalchemy model, and model_str
    is its string name (also capitalized).
    """
    assert id >= 0, "ID can't be negative"
    filter_query = db.query(model).filter(model.id == id)
    item = filter_query.first()
    if item is None:
        raise ItemNotFoundException(model_str, id)
    return item, filter_query


def get_many(
    db: "Session",
    limit: int,
    model,
    skip: int = 0,
):
    """Base get many function. 'model' is the sqlalchemy model."""
    assert limit > 0
    if skip == 0:
        return db.query(model).limit(limit).all()
    else:
        return db.query(model).limit(limit).offset(skip).all()


def get_icon(
    endpoint: str,
    id: int,
    plural_len: int = 1,
) -> FileResponse:
    """Base get icon function.
    Get the icon of the 'endpoint' item with id 'id'.
    """
    assert isinstance(id, int), "ID must be an integer"
    assert id >= 0, "ID can't be negative"
    path = os.path.join(ICONS_FOLDER, f"{endpoint}/{id}.png")
    if not os.path.exists(path):
        assert plural_len >= 0
        model_str = endpoint[:-plural_len] if plural_len > 0 else endpoint
        raise ItemNotFoundException(f"{model_str.capitalize()} image", id)
    return FileResponse(path)


def get_id(
    db: "Session",
    model,
    model_str: str,
    name: str,
    name_col: str = "name",
) -> int:
    """Base get id function.
    Get the id of the item whose name is 'name'.
    """
    assert name_col in {"name", "filename"}
    item = db.query(model).filter(getattr(model, name_col) == name).first()
    if item is None:
        raise NameNotFoundException(model_str, name)
    return item.id


def update_one(
    db: "Session",
    schema_create,
    model,
    model_str: str,
    id: int,
    new_id: int | None = None,
):
    """Base update one (item) function."""
    _, select_query = filter_one(model, model_str, id, db)

    new_info = {"id": new_id if new_id is not None else id} | schema_create.model_dump()

    select_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


def update_many(
    db: "Session",
    model,
    filter,
    update_f,
) -> None:
    """Customazible UPDATE query function."""
    records = db.query(model).filter(filter).all()
    for record in records:
        update_f(record)
    db.commit()


def add_commit_refresh(db: "Session", model) -> None:
    """Add and commit a sqlalchemy change, and then refresh."""
    db.add(model)
    db.commit()
    db.refresh(model)


# * Specific endpoint functions


def dbd_version_str_to_id(s: str) -> int:
    """Converts a DBDVersion string to a DBDVersion id."""
    return parse_or_raise(
        requests.get(
            endp(f"{EP.DBD_VERSION}/id"),
            params={"dbd_version_str": s},
        )
    )


def get_types(db: "Session", type_sqla_model):
    """Base get item types function."""
    assert type_sqla_model.__tablename__ in TN.PREDICTABLE_TYPES
    return get_many(db, 10_000, type_sqla_model)
