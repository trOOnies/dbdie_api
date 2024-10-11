"""Router code for the DBD match."""

from typing import TYPE_CHECKING

import os
from datetime import datetime
from dbdie_classes.schemas.groupings import (
    MatchCreate,
    MatchOut,
    VersionedFolderUpload,
    VersionedMatchOut,
)
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

from backbone.code.matches import (
    form_match, get_versioned_fd_data, upload_dbdv_matches
)
from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    do_count,
    filter_one,
    get_id,
    get_many,
    get_match_img,
    get_req,
    getr,
)
from backbone.exceptions import ValidationException
from backbone.models.groupings import Match
from backbone.options import ENDPOINTS as EP
from backbone.sqla import object_as_dict

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_matches(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(db, Match, text=text)


@router.get("", response_model=list[MatchOut])
def get_matches(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Match, skip)


@router.get("/id", response_model=int)
def get_match_id(filename: str, db: "Session" = Depends(get_db)):
    return get_id(db, Match, "Match", filename, name_col="filename")


@router.get("/image/{id}")
def get_match_image(id: int):
    m = getr(f"{EP.MATCHES}/{id}")
    return get_match_img(m["filename"])


@router.get("/{id}", response_model=MatchOut)
def get_match(id: int, db: "Session" = Depends(get_db)):
    m = filter_one(db, Match, id, "Match")[0]
    m = object_as_dict(m)

    dbdv_id = m["dbdv_id"]
    m["dbd_version"] = (
        None if dbdv_id is None
        else getr(f"{EP.DBD_VERSION}/{dbdv_id}")
    )
    del m["dbdv_id"]

    m = MatchOut(**m)
    return m


@router.post("", response_model=MatchOut)
def create_match(match_create: MatchCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(match_create.filename) is None:
        raise ValidationException("Match filename can't be empty")

    new_match = form_match(match_create)
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

    resp = get_req(EP.MATCHES, new_match.id)
    return resp


@router.post("/vfd", response_model=list[VersionedMatchOut])
def upload_versioned_folder(v_folder: VersionedFolderUpload):
    """Upload DBD-versioned folder that resides in the folder 'versioned',
    and move its matches to 'pending' folder.
    """
    fs, src_fd, dst_fd = get_versioned_fd_data(v_folder)

    # Assert DBD version already exists
    getr(
        f"{EP.DBD_VERSION}/id",
        params={"dbd_version_str": str(v_folder.dbd_version)},
    )

    matches = upload_dbdv_matches(fs, src_fd, dst_fd, v_folder)
    os.rmdir(src_fd)

    return matches


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_match(id: int, match_create: MatchCreate, db: "Session" = Depends(get_db)):
    """Update the information of a DBD match."""
    _, select_query = filter_one(db, Match, id, "Match")

    new_info = {"id": id} | match_create.model_dump()

    del new_info["dbd_version"]
    new_info["dbdv_id"] = (
        None if match_create.dbd_version is None
        else getr(
            f"{EP.DBD_VERSION}/id",
            params={"dbd_version_str": str(match_create.dbd_version)},
        )
    )

    new_info["date_modified"] = datetime.now()

    select_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
