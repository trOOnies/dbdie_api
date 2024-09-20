"""Extra code for the '/extraction' endpoint."""

import pandas as pd
import requests
from typing import TYPE_CHECKING
from dbdie_ml.options.PLAYER_TYPE import KILLER

from backbone.endpoints import endp, parse_or_raise
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from dbdie_ml.classes.base import FullModelType, ModelType


def get_raw_dataset(
    fmts: list["FullModelType"],
    mts: list["ModelType"],
    pts: list[str],
) -> pd.DataFrame:
    data = {
        fmt: parse_or_raise(
            requests.get(
                endp(EP.LABELS),
                json={
                    "is_killer": pt == KILLER,
                    "manual_checks": {mt: False},
                    "limit": 30_000,
                },
            )
        ) for fmt, mt, pt in zip(fmts, mts, pts)
    }
    data = {
        fmt: [(fmtl["match_id"], fmtl["player"]["id"]) for fmtl in fmt_labels]
        for fmt, fmt_labels in data.items()
    }

    # TODO: For now is a FULL, replacing extraction, with an OR gate
    data = sum((tups for tups in data.values()), [])
    raw_dataset = pd.DataFrame(data, columns=["match_id", "label_id"])
    raw_dataset = raw_dataset.drop_duplicates(ignore_index=True)
    del data

    raw_dataset["name"] = raw_dataset["match_id"].map(
        lambda mid: parse_or_raise(
            requests.get(endp(f"{EP.MATCHES}/{mid}"))
        )["filename"]
    )
    return raw_dataset
