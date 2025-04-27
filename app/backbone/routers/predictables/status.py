"""Router code for player end status."""

from typing import TYPE_CHECKING

import requests
from dbdie_classes.schemas.predictables import StatusCreate, StatusOut
from fastapi import APIRouter, Depends, status

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    delete_one,
    do_count,
    endp,
    filter_one,
    get_icon,
    get_many,
    get_req,
    getr,
)
from backbone.exceptions import ValidationException
from backbone.models.predictables import Character, Status
from backbone.options import ENDPOINT as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_statuses(text: str = "", db: "Session" = Depends(get_db)):
    """Count endgame statuses."""
    return do_count(db, Status, text=text)


@router.get("", response_model=list[StatusOut])
def get_statuses(
    limit: int = 10,
    skip: int = 0,
    ifk: bool | None = None,
    db: "Session" = Depends(get_db),
):
    """Get many endgame statuses."""
    return get_many(db, limit, Status, skip, ifk, Character)


@router.get("/{id}", response_model=StatusOut)
def get_status(id: int, db: "Session" = Depends(get_db)):
    """Get an endgame statuses with a certain ID."""
    return filter_one(db, Status, id)[0]


@router.get("/{id}/icon")
def get_status_icon(id: int):
    """Get an endgame status icon."""
    return get_icon("statuses", id, plural_len=2)


@router.post("", response_model=StatusOut, status_code=status.HTTP_201_CREATED)
def create_status(status: StatusCreate, db: "Session" = Depends(get_db)):
    """Create an endgame status."""
    if NOT_WS_PATT.search(status.name) is None:
        raise ValidationException("Status name can't be empty")

    resp = requests.get(endp(f"{EP.CHARACTER}/{status.character_id}"))
    assert resp.status_code == 200

    new_status = status.model_dump() | {"id": getr(f"{EP.STATUS}/count")}
    new_status = Status(**new_status)

    add_commit_refresh(db, new_status)

    return get_req(EP.STATUS, new_status.id)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_status(id: int, db: "Session" = Depends(get_db)):
    """Delete an endgame status."""
    return delete_one(db, Status, id)
