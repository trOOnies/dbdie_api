"""Endpoints-related helper functions"""

import os
import re
from typing import TYPE_CHECKING

import requests
from backbone.config import ST
from backbone.exceptions import ItemNotFoundException, NameNotFoundException
from backbone.options import TABLE_NAMES as TN
from constants import ICONS_FOLDER
from fastapi import Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import func, inspect

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sqlalchemy import Column

ENDPOINT_PATT = re.compile("[a-z]+$")
NOT_WS_PATT = re.compile(r"\S")
NAME_FILTERED_TABLENAMES = {
    TN.ADDONS,
    TN.CHARACTER,
    TN.DBD_VERSION,
    TN.ITEM,
    TN.OFFERING,
    TN.PERKS,
    TN.STATUS,
}


def endp(endpoint: str) -> str:
    """Get full URL of the endpoint"""
    return ST.fastapi_host + endpoint


def get_req(endpoint: str, id: int) -> dict:
    """Request wrapper for a GET request for a type 'endpoint' with an id 'id'."""
    assert ENDPOINT_PATT.match(endpoint)
    resp = requests.get(endp(f"/{endpoint}/{id}"))
    if resp.status_code != status.HTTP_200_OK:
        raise ItemNotFoundException(endpoint.capitalize()[:-1], id)
    return resp.json()


def parse_or_raise(resp, exp_status_code: int = status.HTTP_200_OK):
    """Parse Response as JSON or raise error as exception, depending on status code."""
    if resp.status_code != exp_status_code:
        raise HTTPException(
            status_code=resp.status_code,
            detail=resp.reason,
        )
    return resp.json()


def object_as_dict(obj) -> dict:
    """Convert a sqlalchemy object into a dict."""
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def filter_with_text(query, model, search_text: str):
    """Add a filter to a sqlalchemy query based on the filtered column.
    search_text must already be non-empty.
    """
    search_text = search_text.lower()

    if model.__tablename__ in NAME_FILTERED_TABLENAMES:
        return query.filter(func.lower(model.name).contains(search_text))
    elif model.__tablename__ == TN.MATCHES:
        return query.filter(func.lower(model.filename).contains(search_text))
    else:
        raise NotImplementedError


def add_commit_refresh(model, db: "Session") -> None:
    """Add and commit a sqlalchemy change, and then refresh."""
    db.add(model)
    db.commit()
    db.refresh(model)


# * Base endpoint functions


def fill_cols(model, text: str, is_for_killer: bool | None):
    """Efficient filling of columns in the SQLAlchemy SELECT statement."""
    cols = []

    if is_for_killer is not None:
        cols.append(model.is_for_killer)
    if text != "":
        if model.__tablename__ in NAME_FILTERED_TABLENAMES:
            cols.append(model.name)
        elif model.__tablename__ == TN.MATCHES:
            cols.append(model.filename)
        else:
            raise NotImplementedError

    if not cols:
        cols = [model.id]

    return cols


def fill_cols_custom(
    options: list[tuple["Column", bool | None]],
    default_col: "Column",
):
    """Efficient custom filling of columns in the SQLAlchemy SELECT statement."""
    cols = [c for c, v in options if v is not None]
    if not cols:
        cols = [default_col]
    return cols


def do_count(
    model,
    text: str,
    db: "Session",
    is_for_killer: bool | None = None,
) -> int:
    """Base count function.
    'model' is the sqlalchemy model.
    """
    cols = fill_cols(model, text, is_for_killer)
    query = db.query(*cols)

    if is_for_killer is not None:
        query = query.filter(model.is_for_killer == is_for_killer)
    if text != "":
        query = filter_with_text(query, model, text)

    return query.count()


def filter_one(model, model_str: str, id: int, db: "Session"):
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
    """Base get many function.
    'model' is the sqlalchemy model.
    """
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
    model,
    model_str: str,
    name: str,
    db: "Session",
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
    schema_create,
    model,
    model_str: str,
    id: int,
    db: "Session",
):
    """Base update one (item) function."""
    _, select_query = filter_one(model, model_str, id, db)

    new_info = {"id": id} | schema_create.model_dump()
    print(new_info)

    select_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


# * Specific endpoint functions


def dbd_version_str_to_id(s: str) -> int:
    """Converts a DBDVersion string to a DBDVersion id."""
    dbd_version_id = requests.get(
        endp("/dbd-version/id"),
        params={"dbd_version_str": s},
    )
    dbd_version_id = parse_or_raise(dbd_version_id)
    return dbd_version_id
