"""Endpoints-related helper functions."""

import os
import re
from typing import TYPE_CHECKING

from dbdie_classes.paths import CROPPED_IMG_FD_RP, absp
from fastapi import Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
import requests

from backbone.config import ST
from backbone.exceptions import ItemNotFoundException, NameNotFoundException
from backbone.options import ENDPOINTS as EP
from backbone.options import TABLE_NAMES as TN
from backbone.sqla import get_items_query
from constants import ICONS_FOLDER

if TYPE_CHECKING:
    from dbdie_classes.base import Endpoint, FullEndpoint, PathToFolder
    from sqlalchemy.orm import Session


ENDPOINT_PATT = re.compile(r"\/[a-z\-]+$")
NOT_WS_PATT = re.compile(r"\S")


def endp(endpoint: "Endpoint") -> "FullEndpoint":
    """Get full URL of the endpoint."""
    return ST.fastapi_host + endpoint


def mlendp(endpoint: "Endpoint") -> "FullEndpoint":
    """Get full URL of the ML endpoint."""
    return ST.ml_host + endpoint


def get_req(endpoint: "Endpoint", id: int) -> dict:
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


def getr(endpoint: "Endpoint", **kwargs):
    """Include the boilerplate for a GET request."""
    return parse_or_raise(
        requests.get(endp(endpoint), **kwargs)
    )


def postr(endpoint: "Endpoint", **kwargs):
    """Include the boilerplate for a POST request."""
    return parse_or_raise(
        requests.post(endp(endpoint), **kwargs),
        exp_status_code=status.HTTP_201_CREATED,
    )


def putr(endpoint: "Endpoint", **kwargs):
    """Include the boilerplate for a PUT request."""
    return parse_or_raise(
        requests.put(endp(endpoint), **kwargs)
    )


# * Base endpoint functions


def filter_one(db: "Session", model, id: int, model_str: str | None = None):
    """Base get one (item) function.

    'model' is the sqlalchemy model, and model_str
    is its string name (also capitalized).
    """
    assert id >= 0, "ID can't be negative"
    filter_query = db.query(model).filter(model.id == id)
    item = filter_query.first()
    if item is None:
        raise ItemNotFoundException(
            (model_str if model_str is not None else model.__tablename__.capitalize()),
            id,
        )
    return item, filter_query


def get_first(
    db: "Session",
    limit: int,
    model,
    skip: int = 0,
    ifk: bool | None = None,
    model_type = None,
    text: str = "",
):
    """Base get first function. 'model' is the sqlalchemy model."""
    query = get_items_query(db, limit, model, skip, ifk, model_type, text)
    return query.first()


def get_many(
    db: "Session",
    limit: int,
    model,
    skip: int = 0,
    ifk: bool | None = None,
    model_type = None,
    text: str = "",
):
    """Base get many function. 'model' is the sqlalchemy model."""
    query = get_items_query(db, limit, model, skip, ifk, model_type, text)
    return query.all()


def do_count(
    db: "Session",
    model,
    ifk: bool | None = None,
    model_type = None,
    text: str = "",
) -> int:
    """Base count function.
    'model' is the sqlalchemy model.
    """
    query = get_items_query(db, 100_000, model, 0, ifk, model_type, text)
    return query.count()


def get_image(
    img_add_path: str,
    model_str: str,
    folder_path: "PathToFolder",
) -> FileResponse:
    """Base get image function.
    Get the image of the 'endpoint' item with id 'id'.
    """
    path = os.path.join(folder_path, img_add_path)
    if not os.path.exists(path):
        raise ItemNotFoundException(f"{model_str} image", id)
    return FileResponse(path)


def get_icon(
    endpoint: "Endpoint",
    id: int,
    plural_len: int = 1,
) -> FileResponse:
    """Base get icon function.
    Get the icon of the 'endpoint' item with id 'id'.
    """
    assert isinstance(id, int), "ID must be an integer"
    assert id >= 0, "ID can't be negative"
    assert plural_len >= 0

    img_add_path = f"{endpoint}/{id}.png"
    model_str = endpoint[:-plural_len] if plural_len > 0 else endpoint
    model_str = model_str.capitalize()

    return get_image(img_add_path, model_str, ICONS_FOLDER)


def get_match_img(filename: str) -> FileResponse:
    """Base get match image function."""
    assert "." not in filename[:-4]
    return get_image(filename, "Match", absp(CROPPED_IMG_FD_RP))


def get_id(
    db: "Session",
    model,
    model_str: str,  # TODO: Get from model
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
    model_str: str,  # TODO: Get from model
    id: int,
    new_id: int | None = None,
) -> Response:
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
    return getr(f"{EP.DBD_VERSION}/id", params={"dbd_version_str": s})


def get_types(db: "Session", type_sqla_model):
    """Base get item types function."""
    assert type_sqla_model.__tablename__ in TN.PREDICTABLE_TYPES
    return get_many(db, 10_000, type_sqla_model)
