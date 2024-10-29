"""Extra code for the '/labels' endpoint."""

from typing import TYPE_CHECKING

from fastapi import status
from fastapi.exceptions import HTTPException
import os
import pandas as pd

from dbdie_classes.options.FMT import from_fmt
from dbdie_classes.options.SQL_COLS import MT_TO_COLS
from dbdie_classes.paths import LABELS_FD_RP, absp
from dbdie_classes.schemas.groupings import ManualChecksIn

from backbone.endpoints import getr, postr
from backbone.models.groupings import Labels
from backbone.options import ENDPOINTS as EP
from backbone.sqla import fill_cols_custom, soft_bool_filter

if TYPE_CHECKING:
    from dbdie_classes.base import (
        Filename,
        FullModelType,
        IsForKiller,
        ModelType,
        SQLColumn,
    )
    from sqlalchemy.orm import Session


def filter_one_labels_row(
    db: "Session",
    match_id: int,
    player_id: int,
):
    """Labels' `filter_one` equivalent function."""
    filter_query = (
        db.query(Labels)
        .filter(Labels.match_id == match_id)
        .filter(Labels.player_id == player_id)
    )
    item = filter_query.first()
    if item is None:
        print("NOT FOUND")
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Labels with the id ({match_id}, {player_id}) were not found",
        )
    return item, filter_query


def additional_filters(
    query,
    ifk: "IsForKiller" = None,
    manual_checks: ManualChecksIn | None = None,
):
    if ifk is not None:
        query = (
            query.filter(Labels.player_id == 4)
            if ifk
            else query.filter(Labels.player_id < 4)
        )

    if manual_checks is not None and manual_checks.is_init:
        for col, chk in manual_checks.get_filters_conds(Labels):
            if chk:
                query = query.filter(col.is_(True))
            else:
                query = query.filter(soft_bool_filter(col, False))

    return query


def player_to_labels(player: dict) -> dict:
    """Convert dict format from LabelsCreate schema's to Labels model's"""
    labels = {
        "player_id": player["id"],
        "points": player["points"],
    }

    keys_ending_in_id = [
        k for k, v in player.items() if k.endswith("_id") and v is not None
    ]
    if keys_ending_in_id:
        labels = labels | {k[:-3]: player[k] for k in keys_ending_in_id}

    if player["perk_ids"] is not None:
        labels = labels | {f"perks_{i}": v for i, v in enumerate(player["perk_ids"])}
    if player["addon_ids"] is not None:
        labels = labels | {f"addons_{i}": v for i, v in enumerate(player["addon_ids"])}

    return labels


def get_filtered_query(
    ifk: "IsForKiller",
    manual_checks: ManualChecksIn | None,
    default_cols: list,
    force_prepend_default_cols: bool,
    db: "Session",
):
    options = [(Labels.player_id, ifk)]
    if manual_checks is not None and manual_checks.is_init:
        options += manual_checks.get_filters_conds(Labels)

    cols = fill_cols_custom(
        options,
        default_cols=default_cols,
        force_prepend_default_col=force_prepend_default_cols,
    )
    query = db.query(*cols)
    query = additional_filters(query, ifk, manual_checks)

    return query


# * Batch create labels


def handle_opp_crops(df: pd.DataFrame) -> pd.DataFrame:
    """Handle one-per-player crops, that is,
    the ones that can be encoded as (name, player_id, <obj>).
    """
    df["player_id"] = df["name"].str[-7]
    df = df.astype({"player_id": int})
    df["name"] = df["name"].str[:-8] + ".png"
    df = df.rename({"label_id": "character"}, axis=1)
    return df


def handle_mpp_crops(df: pd.DataFrame) -> pd.DataFrame:
    """Handle many-per-player crops, that is,
    the ones that can be encoded as (name, player_id, <obj>_i).
    """
    df["player_id"] = df["name"].str[-7]
    df["perk_id"] = df["name"].str[-5]
    df["name"] = df["name"].str[:-8] + ".png"

    df = df.rename({"perk_id": "perk"}, axis=1)
    df = df.astype({"player_id": int, "perk": int})

    df = pd.get_dummies(df, columns=["perk"])
    assert "perk" not in df.columns

    df = df.astype({f"perks_{i}": int for i in range(4)})
    for i in range(4):
        df[f"perks_{i}"] = df[f"perks_{i}"] * df["label_id"]
    df = df.drop("label_id", axis=1)

    df = df.groupby(["name", "player_id"]).sum()
    df = df.reset_index(drop=False)
    return df


def get_dfs_dict(
    fmts: list["FullModelType"],
    filename: "Filename",
) -> dict["FullModelType", pd.DataFrame]:
    labels_fd = absp(LABELS_FD_RP)
    return {
        fmt: pd.read_csv(
            os.path.join(labels_fd, f"{fmt}/{filename}"),
            usecols=["name", "label_id"],
        )
        for fmt in fmts
    }


def concat_player_types(
    dfs: dict["FullModelType", pd.DataFrame],
    fmt_1: "FullModelType",
    fmt_2: "FullModelType",
    new_fmt: "FullModelType",
) -> None:
    """Concatenate 2 different FullModelTypes.
    Used for concatenating 2 fmts that come from killer and survivor.
    """
    if fmt_1 in dfs and fmt_2 in dfs:
        dfs[new_fmt] = pd.concat((dfs[fmt_1], dfs[fmt_2]), axis=0)
        assert dfs[new_fmt].shape[1] == dfs[fmt_1].shape[1]
        del dfs[fmt_1], dfs[fmt_2]


def join_dfs(dfs: dict["FullModelType", pd.DataFrame]) -> pd.DataFrame:
    """Join DataFrames that have the same kind of index."""
    is_first = True
    fmts = list(dfs.keys())
    for fmt in fmts:
        if is_first:
            joined_df = dfs[fmt].copy()
            is_first = False
        else:
            joined_df = joined_df.join(dfs[fmt])
        del dfs[fmt]
    del dfs
    return joined_df


def process_joined_df(joined_df: pd.DataFrame) -> pd.DataFrame:
    joined_df = joined_df.reset_index(drop=False)

    joined_df["match_id"] = joined_df["name"].map(
        lambda f: getr(f"{EP.MATCHES}/id", params={"filename": f})
    )
    joined_df = joined_df.drop("name", axis=1)
    return joined_df


def post_labels(joined_df: pd.DataFrame) -> None:
    joined_df = joined_df.astype(
        {
            "match_id": int,
            "player_id": int,
            "character": int,
            "perks_0": int,
            "perks_1": int,
            "perks_2": int,
            "perks_3": int,
        }
    )
    for _, row in joined_df.iterrows():
        postr(
            EP.LABELS,
            json={
                "match_id": int(row["match_id"]),
                "player": {
                    "id": int(row["player_id"]),
                    "character_id": int(row["character"]),
                    "perk_ids": [int(row[f"perks_{i}"]) for i in range(4)],
                    "item_id": None,
                    "addon_ids": None,
                    "offering_id": None,
                    "status_id": None,
                    "points": None,
                },
            },
        )


def process_fmt_strict(fmt: "FullModelType") -> tuple["ModelType", list["SQLColumn"]]:
    """Process full model type for the strict update endpoint."""
    mt, _, _ = from_fmt(fmt)
    return mt, MT_TO_COLS[mt]
