from typing import TYPE_CHECKING
from fastapi import Depends, APIRouter
from dbdie_ml.schemas.predictables import DBDVersion

from backbone import models
from backbone.database import get_db
from backbone.exceptions import ItemNotFoundException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{id}", response_model=DBDVersion)
def get_dbd_version_id(id: int, db: "Session" = Depends(get_db)):
    dbdv = db.query(models.DBDVersion).filter(models.DBDVersion.id == id).first()
    if dbdv is None:
        raise ItemNotFoundException("DBD version", id)
    return dbdv


# @router.put("/{id}", status_code=status.HTTP_200_OK)
# def update_dbd_version(id: int, dbdv: DBDVersion, db: "Session" = Depends(get_db)):
#     new_info = dbdv.model_dump()

#     dbdv_query = db.query(models.DBDVersion).filter(models.DBDVersion.id == id)
#     present_dbdv = dbdv_query.first()
#     if present_dbdv is None:
#         raise ItemNotFoundException("DBD version", id)

#     dbdv_query.update(new_info, synchronize_session=False)
#     db.commit()
#     return Response(status_code=status.HTTP_200_OK)
