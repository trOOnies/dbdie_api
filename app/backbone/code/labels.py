import pandas as pd
from dbdie_ml.classes.base import FullModelType


def player_to_labels(player: dict) -> dict:
    """Convert dict format from `LabelsCreate` schema's to `Labels` model's"""
    labels = {
        "player_id": player["id"],
        "points": player["points"],
    }

    keys_ending_in_id = [
        k for k, v in player.items()
        if k.endswith("_id") and v is not None
    ]
    if keys_ending_in_id:
        labels = labels | {
            k[:-3]: keys_ending_in_id[k]
            for k in keys_ending_in_id
        }

    if player["perk_ids"] is not None:
        labels = labels | {f"perk_{i}": v for i, v in enumerate(player["perk_ids"])}
    if player["addon_ids"] is not None:
        labels = labels | {f"addon_{i}": v for i, v in enumerate(player["addon_ids"])}

    return labels


def concat_player_types(
    dfs: dict[str, pd.DataFrame],
    fmt_1: FullModelType,
    fmt_2: FullModelType,
    new_fmt: str,
) -> None:
    """Concatenate 2 different FullModelTypes.
    Used for concatenating 2 fmts that come from killer and survivor.
    """
    if fmt_1 in dfs and fmt_2 in dfs:
        dfs[new_fmt] = pd.concat((dfs[fmt_1], dfs[fmt_2]), axis=1)
        assert dfs[new_fmt].shape[1] == dfs[fmt_1].shape[1]
        del dfs[fmt_1], dfs[fmt_2]
