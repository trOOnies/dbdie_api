"""Router code for the match"""

from typing import TYPE_CHECKING

import os
import re
import requests
import shutil
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
from dbdie_ml.schemas.groupings import (
    MatchCreate,
    MatchOut,
    VersionedFolderUpload,
    VersionedMatchOut,
)
from dbdie_ml.paths import absp, IMG_MAIN_FD_RP
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()

DATE_PATT = re.compile(r"20\d\d-[0-1]\d-[0-3]\d")


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


@router.post("/vfd", response_model=list[VersionedMatchOut])
def upload_versioned_folder(v_folder: VersionedFolderUpload):
    """Upload DBD-versioned folder that resides in the folder 'versioned',
    and move its matches to 'pending' folder.
    """
    src_main_fd = absp(IMG_MAIN_FD_RP)

    src_fd = os.path.join(src_main_fd, f"versioned/{str(v_folder.dbd_version)}")
    assert os.path.isdir(src_fd)
    fs = os.listdir(src_fd)
    assert fs, "Versioned folder cannot be empty."
    dates = [DATE_PATT.search(f).group() for f in fs]

    dst_fd = os.path.join(src_main_fd, "pending")

    parse_or_raise(
        requests.get(
            endp("/dbd-version/id"),
            params={"dbd_version_str": str(v_folder.dbd_version)},
        )
    )

    matches = []
    for f, d in zip(fs, dates):
        matches.append(
            parse_or_raise(
                requests.post(
                    endp("/matches"),
                    json={
                        "filename": f,
                        "match_date": d,
                        "dbd_version": v_folder.dbd_version.dict(),
                        "special_mode": v_folder.special_mode,
                    },
                )
            )
        )
        shutil.move(os.path.join(src_fd, f), os.path.join(dst_fd, f))

    os.rmdir(src_fd)
    return matches
