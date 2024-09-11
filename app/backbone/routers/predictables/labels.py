"""Router code for DBD match labels."""

import os
from typing import TYPE_CHECKING

from datetime import datetime
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
from backbone.endpoints import add_commit_refresh, endp, fill_cols_custom, get_many, parse_or_raise
from backbone.models import Labels
from dbdie_ml.classes.base import FullModelType
from dbdie_ml.options import COMMON_FMT, KILLER_FMT, SURV_FMT
from dbdie_ml.paths import LABELS_FD_RP, absp
from dbdie_ml.schemas.groupings import LabelsCreate, LabelsOut
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()

ALL_FMT = list(set(COMMON_FMT.ALL) | set(KILLER_FMT.ALL) | set(SURV_FMT.ALL))


@router.get("/count", response_model=int)
def count_labels(
    is_killer: bool | None = None,
    manually_checked: bool | None = None,
    db: "Session" = Depends(get_db),
):
    """Count player-centered labels."""
    cols = fill_cols_custom(
        [(Labels.player_id, is_killer), (Labels.manually_checked, manually_checked)],
        default_col=Labels.match_id,
    )
    query = db.query(*cols)

    if is_killer is not None:
        query = (
            query.filter(Labels.player_id == 4)
            if is_killer
            else query.filter(Labels.player_id < 4)
        )
    if manually_checked is not None:
        query = query.filter(Labels.manually_checked == manually_checked)

    return query.count()


@router.get("", response_model=list[LabelsOut])
def get_labels(
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Get many player-centered labels."""
    labels = get_many(db, limit, Labels, skip)
    labels = [LabelsOut.from_labels(lbl) for lbl in labels]
    return labels


@router.get("/filter", response_model=LabelsOut)
def get_label(
    match_id: int,
    player_id: int,
    db: "Session" = Depends(get_db),
):
    """Get player-centered labels with (match_id, player_id)."""
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
    labels = LabelsOut.from_labels(labels)
    return labels


@router.post("", response_model=LabelsOut)
def create_labels(
    labels: LabelsCreate,
    db: "Session" = Depends(get_db),
):
    """Create player-centered labels."""
    new_labels = labels.model_dump()
    new_labels = new_labels | player_to_labels(new_labels["player"])
    del new_labels["player"]
    new_labels = Labels(**new_labels)

    add_commit_refresh(new_labels, db)

    resp = requests.get(
        endp("/labels/filter"),
        params={
            "match_id": new_labels.match_id,
            "player_id": new_labels.player_id,
        },
    )
    return parse_or_raise(resp)


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_create_labels(fmts: list[FullModelType], filename: str):
    """Create player-centered labels from label CSVs."""
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
            dfs[c] = handle_opp_crops(dfs[c])
    concat_player_types(
        dfs,
        SURV_FMT.CHARACTER,
        KILLER_FMT.CHARACTER,
        new_fmt="character",
    )

    for c in [SURV_FMT.PERKS, KILLER_FMT.PERKS]:
        if c in dfs:
            dfs[c] = handle_mpp_crops(dfs[c])
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
    joined_df = process_joined_df(joined_df)

    post_labels(joined_df)

    return Response(status_code=status.HTTP_201_CREATED)


@router.put("/filter", status_code=status.HTTP_200_OK)
def update_labels(
    match_id: int,
    player_id: int,
    perk_ids: list[int],  # TODO: Expand beyond perks
    db: "Session" = Depends(get_db),
):
    """Update the information of a DBD perk."""
    assert len(perk_ids) == 4, "There must be 4 perk IDs"

    filter_query = (
        db.query(Labels)
        .filter(Labels.match_id == match_id)
        .filter(Labels.player_id == player_id)
    )
    new_info = filter_query.first()
    if new_info is None:
        print("NOT FOUND")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Labels with the id ({match_id}, {player_id}) were not found",
        )

    new_info = LabelsOut.from_labels(new_info)
    player = new_info.player
    new_info = new_info.model_dump()

    new_info = new_info | player.to_sqla()
    del new_info["player"]

    new_info["date_modified"] = datetime.now()
    new_info["user_id"] = 1  # TODO: dynamic
    new_info["extractor_id"] = 1  # TODO: dynamic
    new_info["manually_checked"] = True

    filter_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
