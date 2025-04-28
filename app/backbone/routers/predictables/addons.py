"""Router code for DBD addons."""

from typing import TYPE_CHECKING
from dbdie_classes.schemas.predictables import AddonCreate, AddonOut
from dbdie_classes.schemas.types import AddonTypeOut
from fastapi import APIRouter, Depends, status

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    count_with_dbdvr,
    delete_one,
    do_count,
    filter_one,
    filter_with_dbdvr,
    get_icon,
    get_many,
    get_req,
    get_types,
    getr,
)
from backbone.exceptions import ValidationException
from backbone.models.predictables import Addon, AddonType
from backbone.options import ENDPOINT as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=list[AddonOut])
def get_addons(
    limit: int = 10,
    skip: int = 0,
    ifk: bool | None = None,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Addon, skip, ifk, AddonType)


@router.get("/count", response_model=int)
def count_addons(
    ifk: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    return do_count(db, Addon, text=text, ifk=ifk, mt_type=AddonType)


@router.get("/filter-with-dbdvr", response_model=list[AddonOut])
def filter_addons_by_dbdvr(
    dbdv_min_id: int,
    dbdv_max_id: int | None = None,
    db: "Session" = Depends(get_db),
):
    return filter_with_dbdvr(db, Addon, dbdv_min_id, dbdv_max_id)


@router.get("/filter-with-dbdvr/count", response_model=int)
def count_addons_by_dbdvr(
    dbdv_min_id: int,
    dbdv_max_id: int | None = None,
    db: "Session" = Depends(get_db),
):
    return count_with_dbdvr(db, Addon, dbdv_min_id, dbdv_max_id)


@router.get("/types", response_model=list[AddonTypeOut])
def get_addons_types(db: "Session" = Depends(get_db)):
    return get_types(db, AddonType)


@router.get("/types/{id}", response_model=AddonTypeOut)
def get_addon_type(id: int, db: "Session" = Depends(get_db)):
    return filter_one(db, AddonType, id)[0]


@router.get("/{id}/icon")
def get_addon_icon(id: int):
    return get_icon("addons", id)


@router.get("/{id}", response_model=AddonOut)
def get_addon(id: int, db: "Session" = Depends(get_db)):
    return filter_one(db, Addon, id)[0]


@router.post("", response_model=AddonOut, status_code=status.HTTP_201_CREATED)
def create_addon(addon: AddonCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(addon.name) is None:
        raise ValidationException("Addon name can't be empty")

    new_addon = addon.model_dump() | {"id": getr(f"{EP.ADDONS}/count")}
    new_addon = Addon(**new_addon)

    add_commit_refresh(db, new_addon)

    return get_req(EP.ADDONS, new_addon.id)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_addon(id: int, db: "Session" = Depends(get_db)):
    return delete_one(db, Addon, id)
