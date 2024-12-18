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
    get_icon,
    get_many,
    get_req,
    getr,
)
from backbone.exceptions import ItemNotFoundException, ValidationException
from backbone.models.predictables import Character, Status
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_statuses(text: str = "", db: "Session" = Depends(get_db)):
    return do_count(db, Status, text=text)


@router.get("", response_model=list[StatusOut])
def get_statuses(
    limit: int = 10,
    skip: int = 0,
    ifk: bool | None = None,
    db: "Session" = Depends(get_db),
):
    return get_many(db, limit, Status, skip, ifk, Character)


@router.get("/{id}", response_model=StatusOut)
def get_status(id: int, db: "Session" = Depends(get_db)):
    # TODO: Replace with base function
    status_ = (
        db.query(
            Status.id,
            Status.name,
            Status.character_id,
            Status.is_dead,
            Status.dbdv_id,
            Status.emoji,
            Character.ifk,
        )
        .join(Character)
        .filter(Status.id == id)
        .first()
    )
    if status_ is None:
        raise ItemNotFoundException("Status", id)
    return status_


@router.get("/{id}/icon")
def get_status_icon(id: int):
    return get_icon("statuses", id, plural_len=2)


@router.post("", response_model=StatusOut, status_code=status.HTTP_201_CREATED)
def create_status(status: StatusCreate, db: "Session" = Depends(get_db)):
    if NOT_WS_PATT.search(status.name) is None:
        raise ValidationException("Status name can't be empty")

    resp = requests.get(endp(f"{EP.CHARACTER}/{status.character_id}"))
    assert resp.status_code == 200

    new_status = {"id": getr(f"{EP.STATUS}/count")} | status.model_dump()
    new_status = Status(**new_status)

    add_commit_refresh(db, new_status)

    return get_req(EP.STATUS, new_status.id)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_status(id: int, db: "Session" = Depends(get_db)):
    return delete_one(db, Status, "Status", id)
