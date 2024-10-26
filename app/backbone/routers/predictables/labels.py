"""Router code for DBD match labels."""

from typing import TYPE_CHECKING

from datetime import datetime
from fastapi import APIRouter, Depends, Response, status

from dbdie_classes.base import Filename, FullModelType
from dbdie_classes.code.groupings import (
    labels_model_to_checks,
    labels_model_to_labeled_predictables,
)
from dbdie_classes.options import KILLER_FMT, SURV_FMT
from dbdie_classes.options.FMT import ALL as ALL_FMT
from dbdie_classes.schemas.groupings import (
    LabelsCreate,
    LabelsOut,
    ManualChecksIn,
    PlayerIn,
)

from backbone.code.labels import (
    concat_player_types,
    filter_one_labels_row,
    get_dfs_dict,
    get_filtered_query,
    handle_mpp_crops,
    handle_opp_crops,
    join_dfs,
    player_to_labels,
    post_labels,
    process_fmt_strict,
    process_joined_df,
)
from backbone.database import get_db
from backbone.endpoints import add_commit_refresh, getr
from backbone.models.groupings import Labels
from backbone.options import ENDPOINTS as EP
from backbone.sqla import limit_and_skip

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/count", response_model=int)
def count_labels(
    ifk: bool | None = None,
    manual_checks: ManualChecksIn | None = None,
    db: "Session" = Depends(get_db),
):
    """Count player-centered labels."""
    query = get_filtered_query(
        ifk,
        manual_checks,
        default_cols=[Labels.match_id],
        force_prepend_default_cols=False,
        db=db,
    )
    return query.count()


# TODO: Debug the filter so that it is more helpful and convenient
@router.post(
    "/filter-many",
    response_model=list[LabelsOut],
    status_code=status.HTTP_200_OK,
)
def get_labels(
    ifk: bool | None = None,
    manual_checks: ManualChecksIn | None = None,
    limit: int = 10,
    skip: int = 0,
    db: "Session" = Depends(get_db),
):
    """Get many player-centered labels."""
    assert limit > 0

    query = get_filtered_query(
        ifk,
        manual_checks,
        default_cols=(
            [
                Labels.match_id,
                Labels.player_id,
                Labels.date_modified,
                Labels.user_id,
                Labels.extr_id,
            ]
            + labels_model_to_labeled_predictables(Labels)
            + labels_model_to_checks(Labels)
        ),
        force_prepend_default_cols=True,
        db=db,
    )
    labels = limit_and_skip(query, limit, skip).all()

    labels = [LabelsOut.from_labels(lbl) for lbl in labels]
    return labels


@router.get("/filter", response_model=LabelsOut)
def get_label(
    match_id: int,
    player_id: int,
    db: "Session" = Depends(get_db),
):
    """Get player-centered labels with (match_id, player_id)."""
    labels, _ = filter_one_labels_row(db, match_id, player_id)
    labels = LabelsOut.from_labels(labels)
    return labels


@router.post("", response_model=LabelsOut, status_code=status.HTTP_201_CREATED)
def create_labels(
    labels: LabelsCreate,
    db: "Session" = Depends(get_db),
):
    """Create player-centered labels."""
    new_labels = labels.model_dump()
    new_labels = new_labels | player_to_labels(new_labels["player"])
    del new_labels["player"]
    new_labels = Labels(**new_labels)

    add_commit_refresh(db, new_labels)

    return getr(
        f"{EP.LABELS}/filter",
        params={
            "match_id": new_labels.match_id,
            "player_id": new_labels.player_id,
        },
    )


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_create_labels(fmts: list[FullModelType], filename: Filename):
    """Create player-centered labels from label CSVs."""
    assert fmts, "Full model types can't be empty."
    assert all(fmt in ALL_FMT for fmt in fmts)

    # TODO
    # * Additional temporary filter
    assert all(
        fmt
        in {KILLER_FMT.PERKS, SURV_FMT.PERKS, KILLER_FMT.CHARACTER, SURV_FMT.CHARACTER}
        for fmt in fmts
    )

    dfs = get_dfs_dict(fmts, filename)

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
        fmt: df.set_index(["name", "player_id"], drop=True)
        for fmt, df in dfs.items()
    }

    joined_df = join_dfs(dfs)
    joined_df = process_joined_df(joined_df)

    post_labels(joined_df)

    return Response(status_code=status.HTTP_201_CREATED)


@router.put("/predictable/strict", status_code=status.HTTP_200_OK)
def update_labels_strict(
    match_id: int,
    player_id: int,
    fmt: FullModelType,
    value,
    user_id: int,
    extr_id: int,
    db: "Session" = Depends(get_db),
):
    mt, key = process_fmt_strict(fmt)

    new_info, filter_query = filter_one_labels_row(db, match_id, player_id)
    updated_info = {
        key: value,
        "date_modified": datetime.now(),
        "user_id": user_id,
        "extr_id": extr_id,
        f"{mt}_mckd": False,
    }

    filter_query.update(updated_info, synchronize_session=False)
    db.commit()

    print(new_info.match_id, new_info.player_id, updated_info)

    return Response(status_code=status.HTTP_200_OK)


# TODO: Deprecate this strict implementation if the previous one is more correct
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

    new_info, filter_query = filter_one_labels_row(db, match_id, player.id)

    new_info = LabelsOut.from_labels(new_info)
    sql_player = new_info.player
    new_info = new_info.model_dump()
    del new_info["player"]

    new_info = sql_player.flatten_predictables(new_info)
    new_info = new_info | player.to_sqla(fps, strict)

    new_info["date_modified"] = datetime.now()
    new_info["user_id"] = 1  # TODO: dynamic
    new_info["extr_id"] = 1  # TODO: dynamic

    filter_query.update(new_info, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.delete("/", status_code=status.HTTP_200_OK)
def delete_labels(
    match_id: int,
    player_id: int,
    db: "Session" = Depends(get_db),
):
    item, _ = filter_one_labels_row(db, match_id, player_id)
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)
