from typing import TYPE_CHECKING

import requests
from backbone.code.matches import form_match
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    do_count,
    endp,
    get_id,
    get_many,
    get_one,
    get_req,
    object_as_dict,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Match
from dbdie_ml.schemas.groupings import MatchCreate, MatchOut
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_matches(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(Match, text, db)


@router.get("", response_model=list[MatchOut])
def get_matches(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(Match, limit, skip, db)


@router.get("/id", response_model=int)
def get_match_id(filename: str, db: "Session" = Depends(get_db)):
    return get_id(Match, filename, db, name_col="filename")


@router.get("/{id}", response_model=MatchOut)
def get_match(id: int, db: "Session" = Depends(get_db)):
    m = get_one(Match, "Match", id, db)
    m = object_as_dict(m)

    dbdv_id = m["dbd_version_id"]
    if dbdv_id is None:
        m["dbd_version"] = None
    else:
        resp = requests.get(endp(f"/dbd-version/{dbdv_id}"))
        if resp.status_code == status.HTTP_404_NOT_FOUND:
            raise ItemNotFoundException("DBD version", dbdv_id)
        m["dbd_version"] = resp.json()

    del m["dbd_version_id"]

    m = MatchOut(**m)
    return m


@router.post("", response_model=MatchOut)
def create_match(match: MatchCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(match.filename) is None:
        raise ValidationException("Match filename can't be empty")

    new_match = form_match(match)
    new_match = Match(**new_match)

    db.add(new_match)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            (
                "There was an error commiting the match. "
                + "Make sure you are not reuploading an image with an existing filename."
            ),
        ) from e
    db.refresh(new_match)

    resp = get_req("matches", new_match.id)
    return resp
