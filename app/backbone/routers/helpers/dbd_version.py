"""Router code for DBD version"""

from typing import TYPE_CHECKING

from backbone.database import get_db
from backbone.endpoints import do_count, filter_one, get_id, get_many
from backbone.models import DBDVersion
from dbdie_ml.schemas.predictables import DBDVersionCreate, DBDVersionOut
from fastapi import APIRouter, Depends, Response, status

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_dbd_versions(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(DBDVersion, text, db)


@router.get("", response_model=list[DBDVersionOut])
def get_dbd_versions(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    return get_many(db, limit, DBDVersion, skip)


@router.get("/id", response_model=int)
def get_dbd_version_id(dbd_version_str: str, db: "Session" = Depends(get_db)):
    return get_id(DBDVersion, "DBD version", dbd_version_str, db)


@router.get("/{id}", response_model=DBDVersionOut)
def get_dbd_version(id: int, db: "Session" = Depends(get_db)):
    return filter_one(DBDVersion, "DBD version", id, db)[0]


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_dbd_version(
    id: int,
    dbdv: DBDVersionCreate,
    db: "Session" = Depends(get_db),
):
    _, dbdv_query = filter_one(DBDVersion, "DBD version", id, db)

    new_info = {"id": id} | dbdv.model_dump()
    dbdv_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
