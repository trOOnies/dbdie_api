from typing import TYPE_CHECKING

import requests
from backbone.code.labels import player_to_labels
from backbone.database import get_db
from backbone.endpoints import endp
from backbone.models import Labels
from dbdie_ml.schemas.groupings import LabelsCreate, LabelsOut, PlayerIn
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_labels(db: "Session" = Depends(get_db)):
    query = db.query(Labels.match_id)
    return query.count()


@router.get("", response_model=LabelsOut)
def get_labels(
    match_id: int,
    player_id: int,
    db: "Session" = Depends(get_db),
):
    print("HEY")
    labels = (
        db.query(Labels)
        .filter(Labels.match_id == match_id)
        .filter(Labels.player_id == player_id)
        .first()
    )
    if labels is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Labels with the id ({match_id}, {player_id}) were not found",
        )
    labels = LabelsOut(
        match_id=labels.match_id,
        player=PlayerIn.from_labels(labels),
        date_modified=labels.date_modified,
    )
    return labels


@router.post("", response_model=LabelsOut)
def create_labels(
    labels: LabelsCreate,
    db: "Session" = Depends(get_db),
):
    new_labels = labels.model_dump()
    new_labels = new_labels | player_to_labels(new_labels["player"])
    del new_labels["player"]
    new_labels = Labels(**new_labels)

    db.add(new_labels)
    db.commit()
    db.refresh(new_labels)

    resp = requests.get(
        endp("/labels"),
        params={
            "match_id": new_labels.match_id,
            "player_id": new_labels.player_id,
        },
    )
    if resp.status_code != status.HTTP_200_OK:
        raise HTTPException(resp.status_code, resp.json()["detail"])
    return resp.json()
