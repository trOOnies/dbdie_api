"""Router code for DBD version"""

from typing import TYPE_CHECKING
from dbdie_classes.schemas.helpers import DBDVersionCreate, DBDVersionOut
from fastapi import APIRouter, Depends, Response, status

from backbone.database import get_db
from backbone.endpoints import (
    add_commit_refresh,
    do_count,
    filter_one,
    get_id,
    get_many,
    get_req,
    getr,
    NOT_WS_PATT,
)
from backbone.exceptions import ValidationException
from backbone.models.helpers import DBDVersion
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_dbdvs(
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count DBD versions."""
    return do_count(db, DBDVersion, text=text)


@router.get("", response_model=list[DBDVersionOut])
def get_dbdvs(
    limit: int = 10, 
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Get many DBD versions."""
    return get_many(db, limit, DBDVersion, skip)


@router.get("/id", response_model=int)
def get_dbdv_id(
    dbdv_str: str,
    db: "Session" = Depends(get_db),
):
    """Get DBD version id from its string form."""
    return get_id(db, DBDVersion, "DBD version", dbdv_str)


@router.get("/{id}", response_model=DBDVersionOut)
def get_dbdv(
    id: int,
    db: "Session" = Depends(get_db),
):
    """Get a certain DBD version with its id."""
    return filter_one(db, DBDVersion, id, "DBD version")[0]


@router.post("", response_model=DBDVersionOut, status_code=status.HTTP_201_CREATED)
def create_dbdv(
    dbdv: DBDVersionCreate,
    db: "Session" = Depends(get_db),
):
    """Create DBD version."""
    if NOT_WS_PATT.search(dbdv.name) is None:
        raise ValidationException("DBD version name can't be empty")

    new_dbdv = {"id": getr(f"{EP.DBD_VERSION}/count")} | dbdv.model_dump()
    new_dbdv = DBDVersion(**new_dbdv)

    add_commit_refresh(db, new_dbdv)

    return get_req(EP.DBD_VERSION, new_dbdv.id)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_dbdv(
    id: int,
    dbdv: DBDVersionCreate,
    db: "Session" = Depends(get_db),
):
    """Update a DBD version."""
    _, dbdv_query = filter_one(db, DBDVersion, id, "DBD version")

    new_info = {"id": id} | dbdv.model_dump()
    dbdv_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
