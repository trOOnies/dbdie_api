from typing import TYPE_CHECKING

import requests
from backbone.code.matches import form_match
from backbone.config import endp
from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, filter_with_text, get_req
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models import Match
from backbone.utils import object_as_dict
from dbdie_ml.schemas.groupings import MatchCreate, MatchOut
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_matches(text: str = "", db: "Session" = Depends(get_db)):
    query = db.query(Match)
    if text != "":
        query = filter_with_text(query, text, use_model="match")
    return query.count()


@router.get("", response_model=list[MatchOut])
def get_matches(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    items = db.query(Match).limit(limit).offset(skip).all()
    return items


@router.get("/{id}", response_model=MatchOut)
def get_match(id: int, db: "Session" = Depends(get_db)):
    match = db.query(Match).filter(Match.id == id).first()
    if match is None:
        raise ItemNotFoundException("Match", id)

    match = object_as_dict(match)

    dbdv_id = match["dbd_version_id"]
    if dbdv_id is None:
        match["dbd_version"] = None
    else:
        resp = requests.get(endp(f"/dbd-version/{dbdv_id}"))
        if resp.status_code == status.HTTP_404_NOT_FOUND:
            raise ItemNotFoundException("DBD version", dbdv_id)
        match["dbd_version"] = resp.json()

    del match["dbd_version_id"]

    match = MatchOut(**match)
    return match


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
