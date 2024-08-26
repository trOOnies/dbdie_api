import os
from typing import TYPE_CHECKING

import requests
from backbone.config import endp
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, filter_with_text, get_req
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Addon
from constants import ICONS_FOLDER
from dbdie_ml.schemas.predictables import AddonCreate, AddonOut
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_addons(text: str = "", db: "Session" = Depends(get_db)):
    query = db.query(Addon)
    if text != "":
        query = filter_with_text(query, text, use_model="addon")
    return query.count()


@router.get("", response_model=list[AddonOut])
def get_addons(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    addons = db.query(Addon).limit(limit).offset(skip).all()
    return addons


@router.get("/{id}", response_model=AddonOut)
def get_addon(id: int, db: "Session" = Depends(get_db)):
    addon = db.query(Addon).filter(Addon.id == id).first()
    if addon is None:
        raise ItemNotFoundException("Addon", id)
    return addon


@router.get("/{id}/image")
def get_addon_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"addons/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Addon image", id)
    return FileResponse(path)


@router.post("", response_model=AddonOut)
def create_addon(addon: AddonCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(addon.name) is None:
        raise ValidationException("Addon name can't be empty")

    get_req("characters", addon.user_id)
    # TODO: assert type_id exists

    new_addon = addon.model_dump()
    new_addon = {"id": requests.get(endp("/addons/count")).json()} | new_addon
    new_addon = Addon(**new_addon)

    db.add(new_addon)
    db.commit()
    db.refresh(new_addon)

    return get_req("addons", new_addon.id)
