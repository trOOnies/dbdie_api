"""Router code for the match"""

from typing import TYPE_CHECKING

import requests
from backbone.code.matches import form_match
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    do_count,
    endp,
    filter_one,
    get_id,
    get_many,
    get_req,
    object_as_dict,
    parse_or_raise,
)
from backbone.exceptions import ValidationException
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
    return get_many(db, limit, Match, skip)


@router.get("/id", response_model=int)
def get_match_id(filename: str, db: "Session" = Depends(get_db)):
    return get_id(Match, "Match", filename, db, name_col="filename")


@router.get("/{id}", response_model=MatchOut)
def get_match(id: int, db: "Session" = Depends(get_db)):
    m = filter_one(Match, "Match", id, db)[0]
    m = object_as_dict(m)

    dbdv_id = m["dbd_version_id"]
    if dbdv_id is None:
        m["dbd_version"] = None
    else:
        resp = requests.get(endp(f"/dbd-version/{dbdv_id}"))
        m["dbd_version"] = parse_or_raise(resp)

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
