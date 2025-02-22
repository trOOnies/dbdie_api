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
        print(f"WRONG STATUS CODE: {resp.status_code} (expected: {exp_status_code})")
        raise HTTPException(
            status_code=resp.status_code,
            detail=resp.reason,
        )
    return resp.json()


# * Simpler HTTP requests


def getr(endpoint: "Endpoint", ml: bool = False, **kwargs):
    """Include the boilerplate for a GET request."""
    f = mlendp if ml else endp
    return parse_or_raise(
        requests.get(f(endpoint), **kwargs)
    )


def postr(endpoint: "Endpoint", ml: bool = False, **kwargs):
    """Include the boilerplate for a POST request."""
    f = mlendp if ml else endp
    return parse_or_raise(
        requests.post(f(endpoint), **kwargs),
        exp_status_code=status.HTTP_201_CREATED,
    )


def putr(endpoint: "Endpoint", ml: bool = False, **kwargs):
    """Include the boilerplate for a PUT request."""
    f = mlendp if ml else endp
    return parse_or_raise(
        requests.put(f(endpoint), **kwargs)
    )


# * Base endpoint functions


def filter_one(
    db: "Session",
    model,
    id: int,
    model_str: str | None = None,
):
    """Base get one (item) function.

    `model` is the SQLAlchemy model, and `model_str`
    is its string name (also capitalized).
    """
    assert id >= 0, "ID can't be negative"
    filter_query = db.query(model).filter(model.id == id)
    item = filter_query.first()
    if item is None:
        item_type = (
            model_str if model_str is not None
            else model.__tablename__.capitalize()
        )
        raise ItemNotFoundException(item_type, id)
    return item, filter_query


def get_first(
    db: "Session",
    limit: int,
    model,
    skip: int = 0,
    ifk: bool | None = None,
    mt = None,
    text: str = "",
):
    """Base get first function. 'model' is the sqlalchemy model."""
    query = get_items_query(db, limit, model, skip, ifk, mt, text)
    return query.first()


def get_many(
    db: "Session",
    limit: int,
    model,
    skip: int = 0,
    ifk: bool | None = None,
    mt = None,
    text: str = "",
):
    """Base get many function. 'model' is the sqlalchemy model."""
    query = get_items_query(db, limit, model, skip, ifk, mt, text)
    return query.all()


def do_count(
    db: "Session",
    model,
    ifk: bool | None = None,
    mt_type = None,
    text: str = "",
) -> int:
    """Base count function.
    'model' is the sqlalchemy model.
    """
    query = get_items_query(db, 100_000, model, 0, ifk, mt_type, text)
    return query.count()


def get_image(
    id: int | str,
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

    return get_image(id, img_add_path, model_str, ICONS_FOLDER)


def get_match_img(filename: str) -> FileResponse:
    """Base get match image function."""
    assert "." not in filename[:-4]
    return get_image(filename, filename, "Match", absp(CROPPED_IMG_FD_RP))


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
    _, select_query = filter_one(db, model, id, model_str)

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


def update_one_strict(
    db: "Session",
    model,
    model_str: str,  # TODO: Get from model
    id: int,
    updatable_cols: list[str],
    user_key: str,
    user_value,
) -> Response:
    """Base update one (item) function, but only allows to edit a single column."""
    assert updatable_cols
    assert user_key in updatable_cols

    _, select_query = filter_one(db, model, id, model_str)

    new_info = {user_key: user_value}
    select_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


def add_commit_refresh(db: "Session", model) -> None:
    """Add and commit a sqlalchemy change, and then refresh."""
    db.add(model)
    db.commit()
    db.refresh(model)


def delete_one(
    db: "Session",
    model,
    model_str: str,  # TODO: Get from model
    id: int,
) -> Response:
    """Base delete one (item) function."""
    item, _ = filter_one(db, model, id, model_str)
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)


# * Specific endpoint functions


def dbdv_str_to_id(s: str) -> int:
    """Converts a DBDVersion string to a DBDVersion id."""
    return getr(f"{EP.DBD_VERSION}/id", params={"dbdv_str": s})


def get_types(db: "Session", type_sqla_model):
    """Base get item types function."""
    assert type_sqla_model.__tablename__ in TN.PREDICTABLE_TYPES
    return get_many(db, 10_000, type_sqla_model)
