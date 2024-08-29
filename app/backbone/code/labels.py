from typing import TYPE_CHECKING

import pandas as pd
from dbdie_ml.options import KILLER_FMT, SURV_FMT

if TYPE_CHECKING:
    from dbdie_ml.classes.base import FullModelType


def player_to_labels(player: dict) -> dict:
    """Convert dict format from `LabelsCreate` schema's to `Labels` model's"""
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


# * Batch create labels


def handle_opp_crops(dfs: dict[str, pd.DataFrame]) -> None:
    """Handle one-per-player crops, that is,
    the ones that can be encoded as (name, player_id, <obj>).
    """
    for c in [SURV_FMT.CHARACTER, KILLER_FMT.CHARACTER]:
        if c in dfs:
            dfs[c]["player_id"] = dfs[c]["name"].str[-7]
            dfs[c] = dfs[c].astype({"player_id": int})
            dfs[c]["name"] = dfs[c]["name"].str[:-8] + ".png"
            dfs[c] = dfs[c].rename({"label_id": "character"}, axis=1)


def handle_mpp_crops(dfs: dict[str, pd.DataFrame]) -> None:
    """Handle many-per-player crops, that is,
    the ones that can be encoded as (name, player_id, <obj>_i).
    """
    for c in [SURV_FMT.PERKS, KILLER_FMT.PERKS]:
        if c in dfs:
            dfs[c]["player_id"] = dfs[c]["name"].str[-7]
            dfs[c]["perk_id"] = dfs[c]["name"].str[-5]
            dfs[c]["name"] = dfs[c]["name"].str[:-8] + ".png"

            dfs[c] = dfs[c].rename({"perk_id": "perk"}, axis=1)
            dfs[c] = dfs[c].astype({"player_id": int, "perk": int})

            dfs[c] = pd.get_dummies(dfs[c], columns=["perk"])
            assert "perk" not in dfs[c].columns

            dfs[c] = dfs[c].astype({f"perk_{i}": int for i in range(4)})
            for i in range(4):
                dfs[c][f"perk_{i}"] = dfs[c][f"perk_{i}"] * dfs[c]["label_id"]
            dfs[c] = dfs[c].drop("label_id", axis=1)

            dfs[c] = dfs[c].groupby(["name", "player_id"]).sum()
            dfs[c] = dfs[c].reset_index(drop=False)


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
    for fmt in dfs:
        if is_first:
            joined_df = dfs[fmt].copy()
            is_first = False
        else:
            joined_df = joined_df.join(dfs[fmt])
        dfs[fmt] = None
    del dfs
    return joined_df
