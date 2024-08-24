import requests
from typing import TYPE_CHECKING

from fastapi import Depends, APIRouter, status
from fastapi.exceptions import HTTPException
from dbdie_ml.schemas.groupings import MatchCreate, MatchOut
from dbdie_ml.classes.version import DBDVersion

from backbone.database import get_db
from backbone.endpoints import NOT_WS_PATT, req_wrap, filter_with_text
from backbone.config import endp
from backbone.exceptions import ItemNotFoundException
from backbone import models

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_matches(text: str = "", db: "Session" = Depends(get_db)):
    query = db.query(models.Match)
    if text != "":
        query = filter_with_text(query, text, use_model="match")
    return query.count()


@router.get("/{id}", response_model=MatchOut)
def get_match(id: int, db: "Session" = Depends(get_db)):
    match = (
        db.query(models.Match)
        .filter(models.Match.id == id)
        .join(models.DBDVersion)
        .first()
    )
    if match is None:
        raise ItemNotFoundException("Match", id)
    return match


@router.post("", response_model=MatchOut)
def create_match(match: MatchCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(match.filename) is None:
        return status.HTTP_400_BAD_REQUEST

    new_match = match.model_dump()

    new_match = {"id": requests.get(endp("/matches/count")).json()} | new_match

    if new_match["dbd_version"] is not None:
        dbdv = str(DBDVersion(**new_match["dbd_version"]))
        payload = {"dbd_version_str": dbdv}

        resp = requests.get(endp("/dbd-version/id"), params=payload)
        if resp.status_code != status.HTTP_200_OK:
            raise HTTPException(resp.status_code, resp.json()["detail"])

        new_match["dbd_version_id"] = resp.json()
    else:
        new_match["dbd_version_id"] = None
    del new_match["dbd_version"]

    new_match = models.Match(**new_match)

    db.add(new_match)
    try:
        db.commit()
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            (
                "There was an error commiting the match. "
                + "Make sure you are not reuploading an image with an existing filename."
            ),
        )
    db.refresh(new_match)

    resp = req_wrap("matches", new_match.id)
    return resp
