from typing import TYPE_CHECKING
from fastapi import Depends, APIRouter
from dbdie_ml import schemas
from dbdie_ml.classes import DBDVersion

from backbone import models
from backbone.database import get_db
from backbone.exceptions import ItemNotFoundException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{id}", response_model=schemas.Item)
def get_dbd_version_id(
    major: int | str,
    minor: int | str,
    patch: int | str,
    db: "Session" = Depends(get_db),
):
    # TODO
    dbd_version = DBDVersion(major, minor, patch)
    item = db.query(models.DBDVersion).filter(models.DBDVersion.id == id).first()
    if item is None:
        raise ItemNotFoundException("DBD version", id)
    return item
