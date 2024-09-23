"""Router code for DBD version"""

import requests
from typing import TYPE_CHECKING
from dbdie_classes.schemas.predictables import DBDVersionCreate, DBDVersionOut
from fastapi import APIRouter, Depends, Response, status

from backbone.database import get_db
from backbone.endpoints import (
    add_commit_refresh,
    do_count,
    endp,
    filter_one,
    get_id,
    get_many,
    get_req,
    NOT_WS_PATT,
)
from backbone.exceptions import ValidationException
from backbone.models.groupings import DBDVersion
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_dbd_versions(text: str = "", db: "Session" = Depends(get_db)):
    """Count DBD versions."""
    return do_count(db, DBDVersion, text)


@router.get("", response_model=list[DBDVersionOut])
def get_dbd_versions(limit: int = 10, skip: int = 0, db: "Session" = Depends(get_db)):
    """Get many DBD versions."""
    return get_many(db, limit, DBDVersion, skip)


@router.get("/id", response_model=int)
def get_dbd_version_id(dbd_version_str: str, db: "Session" = Depends(get_db)):
    """Get DBD version id from its string form."""
    return get_id(db, DBDVersion, "DBD version", dbd_version_str)


@router.get("/{id}", response_model=DBDVersionOut)
def get_dbd_version(id: int, db: "Session" = Depends(get_db)):
    """Get a certain DBD version with its id."""
    return filter_one(db, DBDVersion, "DBD version", id)[0]


@router.post("", response_model=DBDVersionOut)
def create_dbd_version(dbdv: DBDVersionCreate, db: "Session" = Depends(get_db)):
    """Create DBD version."""
    if NOT_WS_PATT.search(dbdv.name) is None:
        raise ValidationException("DBD version name can't be empty")

    new_dbdv = {"id": requests.get(endp(f"{EP.DBD_VERSION}/count")).json()} | dbdv.model_dump()
    new_dbdv = DBDVersion(**new_dbdv)

    add_commit_refresh(db, new_dbdv)

    return get_req(EP.DBD_VERSION, new_dbdv.id)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_dbd_version(
    id: int,
    dbdv: DBDVersionCreate,
    db: "Session" = Depends(get_db),
):
    """Update a DBD version."""
    _, dbdv_query = filter_one(db, DBDVersion, "DBD version", id)

    new_info = {"id": id} | dbdv.model_dump()
    dbdv_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
