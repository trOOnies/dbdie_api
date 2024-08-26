import requests
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from dbdie_ml.schemas.groupings import LabelsCreate, LabelsOut, PlayerIn

from backbone.database import get_db
from backbone.models import Labels
from backbone.endpoints import endp

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
        player=PlayerIn(
            id=labels.player_id,
            character_id=labels.character,
            perk_ids=[getattr(labels, f"perk_{i}") for i in range(4)],
            item_id=labels.item,
            addon_ids=[labels.addon_0, labels.addon_1],
            offering_id=labels.offering,
            status_id=labels.status,
            points=labels.points,
        ),  # TODO: as 2 bidirectional methods
        date_modified=labels.date_modified,
    )
    return labels


def player_to_labels(labels: dict) -> dict:
    labels["player_id"] = labels["player"]["id"]
    del labels["player"]["id"]

    labels = labels | {
        k[:-3]: v for k, v in labels["player"].items()
        if k.endswith("_id")
    }
    labels = labels | {
        f"perk_{i}": v
        for i, v in enumerate(labels["player"]["perk_ids"])
    }
    labels = labels | {
        f"addon_{i}": v
        for i, v in enumerate(labels["player"]["addon_ids"])
    }
    labels = labels | {"points": labels["player"]["points"]}

    del labels["player"]
    return labels


@router.post("", response_model=LabelsOut)
def create_labels(
    labels: LabelsCreate,
    db: "Session" = Depends(get_db),
):
    new_labels = labels.model_dump()
    new_labels = player_to_labels(new_labels)
    new_labels = Labels(**new_labels)

    db.add(new_labels)
    db.commit()
    db.refresh(new_labels)

    resp = requests.get(
        endp("/labels"),
        params={
            "match_id": new_labels.match_id,
            "player_id": new_labels.player_id,
        }
    )
    if resp.status_code != status.HTTP_200_OK:
        raise HTTPException(resp.status_code, resp.json()["detail"])
    return resp.json()
