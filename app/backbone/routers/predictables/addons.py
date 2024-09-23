"""Router code for DBD addons."""

import requests
from typing import TYPE_CHECKING
from dbdie_classes.schemas.predictables import AddonCreate, AddonOut, AddonTypeOut
from fastapi import APIRouter, Depends

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    dbd_version_str_to_id,
    do_count,
    endp,
    filter_one,
    get_icon,
    get_many,
    get_req,
    get_types,
)
from backbone.exceptions import ValidationException
from backbone.models.predictables import Addon, AddonType
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_addons(
    is_for_killer: bool | None = None,
    text: str = "",
    db: "Session" = Depends(get_db),
):
    return do_count(db, Addon, text, is_for_killer, AddonType)


@router.get("", response_model=list[AddonOut])
def get_addons(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    return get_many(db, limit, Addon, skip)


@router.get("/types", response_model=list[AddonTypeOut])
def get_addons_types(db: "Session" = Depends(get_db)):
    return get_types(db, AddonType)


@router.get("/{id}", response_model=AddonOut)
def get_addon(id: int, db: "Session" = Depends(get_db)):
    return filter_one(db, Addon, "Addon", id)[0]


@router.get("/{id}/icon")
def get_addon_icon(id: int):
    return get_icon("addons", id)


@router.post("", response_model=AddonOut)
def create_addon(addon: AddonCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(addon.name) is None:
        raise ValidationException("Addon name can't be empty")

    get_req(EP.CHARACTER, addon.user_id)
    # TODO: assert type_id exists

    new_addon = addon.model_dump()
    new_addon = {"id": requests.get(endp(f"{EP.ADDONS}/count")).json()} | new_addon
    new_addon["dbd_version_id"] = (
        dbd_version_str_to_id(new_addon["dbd_version_str"])
        if new_addon["dbd_version_str"] is not None
        else None
    )
    del new_addon["dbd_version_str"]
    new_addon = Addon(**new_addon)

    add_commit_refresh(db, new_addon)

    return get_req(EP.ADDONS, new_addon.id)
