from typing import TYPE_CHECKING

from backbone.database import get_db
from backbone.exceptions import ItemNotFoundException
from backbone.models import DBDVersion
from dbdie_ml.schemas.predictables import DBDVersionCreate, DBDVersionOut
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/id", response_model=int)
def get_dbd_version_id(dbd_version_str: str, db: "Session" = Depends(get_db)):
    dbd_version = (
        db.query(DBDVersion).filter(DBDVersion.name == dbd_version_str).first()
    )
    if dbd_version is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"DBD version '{dbd_version_str}' was not found"
        )
    return dbd_version.id


@router.get("/{id}", response_model=DBDVersionOut)
def get_dbd_version(id: int, db: "Session" = Depends(get_db)):
    dbdv = db.query(DBDVersion).filter(DBDVersion.id == id).first()
    if dbdv is None:
        raise ItemNotFoundException("DBD version", id)
    return dbdv


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_dbd_version(
    id: int,
    dbdv: DBDVersionCreate,
    db: "Session" = Depends(get_db),
):
    dbdv_query = db.query(DBDVersion).filter(DBDVersion.id == id)
    present_dbdv = dbdv_query.first()
    if present_dbdv is None:
        raise ItemNotFoundException("DBD version", id)

    new_info = {"id": id} | dbdv.model_dump()
    new_info = DBDVersion(**new_info)

    dbdv_query.update(new_info, synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)
