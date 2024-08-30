"""Endpoints-related helper functions"""

import os
import re
from typing import TYPE_CHECKING

import requests
from backbone.config import ST
from backbone.exceptions import ItemNotFoundException, NameNotFoundException
from backbone.options import TABLE_NAMES as TN
from constants import ICONS_FOLDER
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import func, inspect

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

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


def parse_or_raise(resp):
    """Parse Response as JSON or raise error as exception, depending on status code."""
    if resp.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=resp.status_code,
            detail=resp.reason,
        )
    return resp.json()


def object_as_dict(obj) -> dict:
    """Convert a sqlalchemy object into a dict."""
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def filter_with_text(db: "Session", search_text: str, model):
    """Add a filter to a sqlalchemy query based on the filtered column.
    search_text must already be non-empty.
    """
    search_text = search_text.lower()

    if model.__tablename__ in NAME_FILTERED_TABLENAMES:
        query = db.query(model.name)
        return query.filter(func.lower(model.name).contains(search_text))
    elif model.__tablename__ == TN.MATCHES:
        query = db.query(model.filename)
        return query.filter(func.lower(model.filename).contains(search_text))
    else:
        raise NotImplementedError


def add_commit_refresh(model, db: "Session") -> None:
    """Add and commit a sqlalchemy change, and then refresh."""
    db.add(model)
    db.commit()
    db.refresh(model)


# * Base endpoint functions


def do_count(model, text: str, db: "Session") -> int:
    """Base count function.
    'model' is the sqlalchemy model.
    """
    if text == "":
        query = db.query(model.id)
    else:
        query = filter_with_text(db, text, model)
    return query.count()


def get_one(model, model_str: str, id: int, db: "Session"):
    """Base get one (item) function.
    'model' is the sqlalchemy model, and model_str
    is its string name (also capitalized).
    """
    item = db.query(model).filter(model.id == id).first()
    if item is None:
        raise ItemNotFoundException(model_str, id)
    return item


def get_many(
    model,
    limit: int,
    skip: int,
    db: "Session",
):
    """Base get many function.
    'model' is the sqlalchemy model.
    """
    return db.query(model).limit(limit).offset(skip).all()


def get_icon(
    endpoint: str,
    id: int,
    plural_len: int = 1,
) -> FileResponse:
    """Base get icon function.
    Get the icon of the 'endpoint' item with id 'id'.
    """
    path = os.path.join(ICONS_FOLDER, f"{endpoint}/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException(f"{endpoint[:-plural_len].capitalize()} image", id)
    return FileResponse(path)


def get_id(model, name: str, db: "Session", name_col: str = "name") -> int:
    """Base get id function.
    Get the id of the item whose name is 'name'.
    """
    assert name_col in {"name", "filename"}
    item = db.query(model).filter(getattr(model, name_col) == name).first()
    if item is None:
        raise NameNotFoundException("DBD version", name)
    return item.id


def dbd_version_str_to_id(s: str) -> int:
    """Converts a DBDVersion string to a DBDVersion id."""
    dbd_version_id = requests.get(
        endp("/dbd-version/id"),
        params={"dbd_version_str": s},
    )
    if dbd_version_id.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"DBD version '{s}' was not found",
        )
    return dbd_version_id.json()
