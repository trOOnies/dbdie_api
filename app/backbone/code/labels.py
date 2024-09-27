"""Extra code for the '/labels' endpoint."""

from typing import TYPE_CHECKING

from dbdie_classes.schemas.groupings import ManualChecksIn
import pandas as pd
import requests

from backbone.endpoints import endp
from backbone.models.groupings import Labels
from backbone.options import ENDPOINTS as EP
from backbone.sqla import fill_cols_custom, soft_bool_filter

if TYPE_CHECKING:
    from dbdie_classes.base import FullModelType
    from sqlalchemy.orm import Session


def additional_filters(
    query,
    is_killer: bool | None = None,
    manual_checks: ManualChecksIn | None = None,
):
    if is_killer is not None:
        query = (
            query.filter(Labels.player_id == 4)
            if is_killer
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
        labels = labels | {f"perk_{i}": v for i, v in enumerate(player["perk_ids"])}
    if player["addon_ids"] is not None:
        labels = labels | {f"addon_{i}": v for i, v in enumerate(player["addon_ids"])}

    return labels


def get_filtered_query(
    is_killer: bool | None,
    manual_checks: ManualChecksIn | None,
    default_cols: list,
    force_prepend_default_cols: bool,
    db: "Session",
):
    options = [(Labels.player_id, is_killer)]
    if manual_checks is not None and manual_checks.is_init:
        options += [
            (col, chk)
            for chk, col in zip(
                manual_checks.checks,
                manual_checks.model_to_cols(Labels),
            )
        ]

    cols = fill_cols_custom(
        options,
        default_cols=default_cols,
        force_prepend_default_col=force_prepend_default_cols,
    )
    query = db.query(*cols)
    query = additional_filters(query, is_killer, manual_checks)

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

    df = df.astype({f"perk_{i}": int for i in range(4)})
    for i in range(4):
        df[f"perk_{i}"] = df[f"perk_{i}"] * df["label_id"]
    df = df.drop("label_id", axis=1)

    df = df.groupby(["name", "player_id"]).sum()
    df = df.reset_index(drop=False)
    return df


def concat_player_types(
    dfs: dict[str, pd.DataFrame],
    fmt_1: "FullModelType",
    fmt_2: "FullModelType",
    new_fmt: str,
) -> None:
    """Concatenate 2 different FullModelTypes.
    Used for concatenating 2 fmts that come from killer and survivor.
    """
    if fmt_1 in dfs and fmt_2 in dfs:
        dfs[new_fmt] = pd.concat((dfs[fmt_1], dfs[fmt_2]), axis=0)
        assert dfs[new_fmt].shape[1] == dfs[fmt_1].shape[1]
        del dfs[fmt_1], dfs[fmt_2]


def join_dfs(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
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
        lambda f: requests.get(
            endp(f"{EP.MATCHES}/id"),
            params={"filename": f},
        ).json(),
    )
    joined_df = joined_df.drop("name", axis=1)
    return joined_df


def post_labels(joined_df: pd.DataFrame) -> None:
    joined_df = joined_df.astype(
        {
            k: int
            for k in [
                "match_id",
                "player_id",
                "character",
                "perk_0",
                "perk_1",
                "perk_2",
                "perk_3",
            ]
        }
    )
    for _, row in joined_df.iterrows():
        requests.post(
            endp(EP.LABELS),
            json={
                "match_id": int(row["match_id"]),
                "player": {
                    "id": int(row["player_id"]),
                    "character_id": int(row["character"]),
                    "perk_ids": [int(row[f"perk_{i}"]) for i in range(4)],
                    "item_id": None,
                    "addon_ids": None,
                    "offering_id": None,
                    "status_id": None,
                    "points": None,
                },
            },
        )
