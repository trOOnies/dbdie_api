"""Router code for DBDIE `CropperSwarm`."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.objects import CropperSwarmCreate, CropperSwarmOut
from fastapi import APIRouter, Depends, status

from backbone.database import get_db
from backbone.endpoints import (
    NOT_WS_PATT,
    add_commit_refresh,
    delete_one,
    do_count,
    filter_one,
    get_many,
    get_req,
    postr,
    update_one,
)
from backbone.exceptions import ValidationException
from backbone.models.objects import CropperSwarm
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/count", response_model=int)
def count_cropper_swarms(
    text: str = "",
    db: "Session" = Depends(get_db),
):
    """Count CropperSwarms."""
    return do_count(db, CropperSwarm, text=text)


@router.get("", response_model=list[CropperSwarmOut])
def get_cropper_swarms(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Query many CropperSwarms."""
    return get_many(db, limit, CropperSwarm, skip)


@router.get("/{id}", response_model=CropperSwarmOut)
def get_cropper_swarm(id: int, db: "Session" = Depends(get_db)):
    """Get a CropperSwarm with an ID."""
    return filter_one(db, CropperSwarm, id)[0]


@router.post("/{id}", response_model=CropperSwarmOut, status_code=status.HTTP_201_CREATED)
def create_cropper_swarm(
    id: int,
    cropper_swarm: CropperSwarmCreate,
    db: "Session" = Depends(get_db),
):
    """Register a CropperSwarm."""
    if NOT_WS_PATT.search(cropper_swarm.name) is None:
        raise ValidationException("CropperSwarm name can't be empty.")

    new_cropper_swarm = {"id": id} | cropper_swarm.model_dump()

    new_cropper_swarm = CropperSwarm(**new_cropper_swarm)
    add_commit_refresh(db, new_cropper_swarm)

    resp = get_req(EP.CROPPER_SWARM, new_cropper_swarm.id)

    postr("/crop/register", ml=True, json=resp)

    return resp


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_cropper_swarm(
    id: int,
    cropper_swarm: CropperSwarmCreate,
    db: "Session" = Depends(get_db),
):
    """Update the information of an InfoCropperSwarm in the database."""
    # TODO: Update its config as well, and only allow sensible modifications.
    return update_one(db, cropper_swarm, CropperSwarm, "CropperSwarm", id)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_cropper_swarm(id: int, db: "Session" = Depends(get_db)):
    return delete_one(db, CropperSwarm, "CropperSwarm", id)
