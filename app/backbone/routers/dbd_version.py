from typing import TYPE_CHECKING
from fastapi import Depends, APIRouter, status
from fastapi.exceptions import HTTPException
from dbdie_ml.schemas.predictables import DBDVersionOut

from backbone import models
from backbone.database import get_db
from backbone.exceptions import ItemNotFoundException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/id", response_model=int)
def get_dbd_version_id(dbd_version_str: str, db: "Session" = Depends(get_db)):
    dbd_version = (
        db
        .query(models.DBDVersion)
        .filter(models.DBDVersion.name == dbd_version_str)
        .first()
    )
    if dbd_version is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"DBD version '{dbd_version_str}' was not found"
        )
    return dbd_version.id


@router.get("/{id}", response_model=DBDVersionOut)
def get_dbd_version(id: int, db: "Session" = Depends(get_db)):
    dbdv = db.query(models.DBDVersion).filter(models.DBDVersion.id == id).first()
    if dbdv is None:
        raise ItemNotFoundException("DBD version", id)
    return dbdv


# @router.put("/{id}", status_code=status.HTTP_200_OK)
# def update_dbd_version(id: int, dbdv: DBDVersionOut, db: "Session" = Depends(get_db)):
#     new_info = dbdv.model_dump()

#     dbdv_query = db.query(models.DBDVersion).filter(models.DBDVersion.id == id)
#     present_dbdv = dbdv_query.first()
#     if present_dbdv is None:
#         raise ItemNotFoundException("DBD version", id)

#     dbdv_query.update(new_info, synchronize_session=False)
#     db.commit()
#     return Response(status_code=status.HTTP_200_OK)
