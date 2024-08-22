import os
import requests
from dbdie_ml import schemas
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, status
from fastapi.responses import FileResponse

from constants import ICONS_FOLDER
from backbone import models
from backbone.config import endp
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, filter_with_text, req_wrap
from backbone.exceptions import ItemNotFoundException

router = APIRouter()


@router.get("/count", response_model=int)
def count_addons(text: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Addon)
    if text != "":
        query = filter_with_text(query, text, use_model="addon")
    return query.count()


@router.get("", response_model=list[schemas.Addon])
def get_addons(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    addons = db.query(models.Addon).limit(limit).offset(skip).all()
    return addons


@router.get("/{id}", response_model=schemas.Addon)
def get_addon(id: int, db: "Session" = Depends(get_db)):
    addon = db.query(models.Addon).filter(models.Addon.id == id).first()
    if addon is None:
        raise ItemNotFoundException("Addon", id)
    return addon


@router.get("/{id}/image")
def get_addon_image(id: int):
    path = os.path.join(ICONS_FOLDER, f"addons/{id}.png")
    if not os.path.exists(path):
        raise ItemNotFoundException("Addon image", id)
    return FileResponse(path)


@router.post("", response_model=schemas.Addon)
def create_addon(addon: schemas.AddonCreate, db: Session = Depends(get_db)):
    if NOT_WS_PATT.search(addon.name) is None:
        return status.HTTP_400_BAD_REQUEST

    req_wrap("characters", addon.user_id)
    # TODO: assert type_id exists

    new_addon = addon.model_dump()
    new_addon["id"] = requests.get(endp("/addons/count")).json()
    new_addon = models.Addon(**new_addon)

    db.add(new_addon)
    db.commit()
    db.refresh(new_addon)

    return req_wrap("addons", new_addon.id)
