from typing import TYPE_CHECKING

import requests
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    do_count,
    endp,
    get_icon,
    get_many,
    get_one,
    get_req,
)
from backbone.exceptions import ValidationException
from backbone.models import Addon
from dbdie_ml.schemas.predictables import AddonCreate, AddonOut
from fastapi import APIRouter, Depends

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_addons(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(Addon, text, db)


@router.get("", response_model=list[AddonOut])
def get_addons(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    return get_many(Addon, limit, skip, db)


@router.get("/{id}", response_model=AddonOut)
def get_addon(id: int, db: "Session" = Depends(get_db)):
    return get_one(Addon, "Addon", id, db)


@router.get("/{id}/icon")
def get_addon_icon(id: int):
    return get_icon("addons", id)


@router.post("", response_model=AddonOut)
def create_addon(addon: AddonCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(addon.name) is None:
        raise ValidationException("Addon name can't be empty")

    get_req("characters", addon.user_id)
    # TODO: assert type_id exists

    new_addon = addon.model_dump()
    new_addon = {"id": requests.get(endp("/addons/count")).json()} | new_addon
    new_addon = Addon(**new_addon)

    add_commit_refresh(new_addon, db)

    return get_req("addons", new_addon.id)
