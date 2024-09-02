"""Router code for match labels"""

import os
from typing import TYPE_CHECKING

import pandas as pd
import requests
from backbone.code.labels import (
    concat_player_types,
    handle_mpp_crops,
    handle_opp_crops,
    join_dfs,
    player_to_labels,
    post_labels,
    process_joined_df,
)
from backbone.database import get_db
from backbone.endpoints import add_commit_refresh, endp, parse_or_raise
from backbone.models import Labels
from dbdie_ml.classes.base import FullModelType
from dbdie_ml.options import COMMON_FMT, KILLER_FMT, SURV_FMT
from dbdie_ml.paths import LABELS_FD_RP, absp
from dbdie_ml.schemas.groupings import LabelsCreate, LabelsOut, PlayerIn
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()

ALL_FMT = list(set(COMMON_FMT.ALL) | set(KILLER_FMT.ALL) | set(SURV_FMT.ALL))


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

    add_commit_refresh(new_labels, db)

    resp = requests.get(
        endp("/labels"),
        params={
            "match_id": new_labels.match_id,
            "player_id": new_labels.player_id,
        },
    )
    return parse_or_raise(resp)


@router.post("/batch", status_code=status.HTTP_200_OK)
def batch_create_labels(fmts: list[FullModelType], filename: str):
    """Create labels from label CSVs."""
    assert fmts, "Full model types can't be empty"
    assert all(fmt in ALL_FMT for fmt in fmts)

    # TODO
    # * Additional temporary filter
    assert all(
        fmt
        in {KILLER_FMT.PERKS, SURV_FMT.PERKS, KILLER_FMT.CHARACTER, SURV_FMT.CHARACTER}
        for fmt in fmts
    )

    dfs = {
        fmt: pd.read_csv(
            os.path.join(absp(LABELS_FD_RP), f"{fmt}/{filename}"),
            usecols=["name", "label_id"],
        )
        for fmt in fmts
    }

    for c in [SURV_FMT.CHARACTER, KILLER_FMT.CHARACTER]:
        if c in dfs:
            handle_opp_crops(dfs[c])
    concat_player_types(
        dfs,
        SURV_FMT.CHARACTER,
        KILLER_FMT.CHARACTER,
        new_fmt="character",
    )

    for c in [SURV_FMT.PERKS, KILLER_FMT.PERKS]:
        if c in dfs:
            handle_mpp_crops(dfs[c])
    concat_player_types(
        dfs,
        SURV_FMT.PERKS,
        KILLER_FMT.PERKS,
        new_fmt="perks",
    )

    dfs = {
        fmt: df.set_index(["name", "player_id"], drop=True) for fmt, df in dfs.items()
    }

    joined_df = join_dfs(dfs)
    process_joined_df(joined_df)

    post_labels(joined_df)

    return Response(status_code=status.HTTP_200_OK)
