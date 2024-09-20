"""Router code for DBD match labels."""

import os
from typing import TYPE_CHECKING

from datetime import datetime
import pandas as pd
import requests
from dbdie_ml.classes.base import FullModelType
from dbdie_ml.options import COMMON_FMT, KILLER_FMT, SURV_FMT
from dbdie_ml.paths import LABELS_FD_RP, absp
from dbdie_ml.schemas.groupings import (
    LabelsCreate,
    LabelsOut,
    ManualChecksIn,
    PlayerIn,
)
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

from backbone.code.labels import (
    concat_player_types,
    get_filtered_query,
    handle_mpp_crops,
    handle_opp_crops,
    join_dfs,
    player_to_labels,
    post_labels,
    process_joined_df,
)
from backbone.database import get_db
from backbone.endpoints import (
    add_commit_refresh,
    endp,
    parse_or_raise,
)
from backbone.models import Labels
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()

ALL_FMT = list(set(COMMON_FMT.ALL) | set(KILLER_FMT.ALL) | set(SURV_FMT.ALL))


@router.get("/count", response_model=int)
def count_labels(
    is_killer: bool | None = None,
    manual_checks: ManualChecksIn | None = None,
    db: "Session" = Depends(get_db),
):
    """Count player-centered labels."""
    query = get_filtered_query(
        is_killer,
        manual_checks,
        default_cols=[Labels.match_id],
        force_prepend_default_cols=False,
        db=db,
    )
    return query.count()


@router.get("", response_model=list[LabelsOut])
def get_labels(
    is_killer: bool | None = None,
    manual_checks: ManualChecksIn | None = None,
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Get many player-centered labels."""
    assert limit > 0

    query = get_filtered_query(
        is_killer,
        manual_checks,
        default_cols=[
            Labels.match_id,
            Labels.player_id,
            Labels.date_modified,
            Labels.user_id,
            Labels.extractor_id,
            Labels.addons_mckd,
            Labels.character_mckd,
            Labels.item_mckd,
            Labels.offering_mckd,
            Labels.perks_mckd,
            Labels.prestige_mckd,
            Labels.points_mckd,
            Labels.status_mckd,
        ],
        force_prepend_default_cols=True,
        db=db,
    )
    if skip == 0:
        labels = query.limit(limit).all()
    else:
        labels = query.limit(limit).offset(skip).all()

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
        endp(f"{EP.LABELS}/filter"),
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


@router.put("/predictable", status_code=status.HTTP_200_OK)
def update_labels(
    match_id: int,
    player: PlayerIn,
    strict: bool = True,
    db: "Session" = Depends(get_db),
):
    """Update the information of predictables."""
    fps = player.filled_predictables()
    if strict:
        assert len(fps) == 1

    filter_query = (
        db.query(Labels)
        .filter(Labels.match_id == match_id)
        .filter(Labels.player_id == player.id)
    )
    new_info = filter_query.first()
    if new_info is None:
        print("NOT FOUND")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Labels with the id ({match_id}, {player.id}) were not found",
        )

    new_info = LabelsOut.from_labels(new_info)
    sql_player = new_info.player
    new_info = new_info.model_dump()
    del new_info["player"]

    new_info = sql_player.flatten_predictables(new_info)
    new_info = new_info | player.to_sqla(fps, strict)

    new_info["date_modified"] = datetime.now()
    new_info["user_id"] = 1  # TODO: dynamic
    new_info["extractor_id"] = 1  # TODO: dynamic

    filter_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)
