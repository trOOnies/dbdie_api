"""Extra code for the '/training' endpoint."""

from copy import deepcopy
import datetime as dt
from dbdie_classes.groupings import PredictableTuples
from dbdie_classes.options import KILLER_FMT
from dbdie_classes.options import SURV_FMT
from dbdie_classes.options.FMT import ALL as ALL_FMTS_ORDERED
from typing import TYPE_CHECKING

from backbone.endpoints import getr, postr, putr
from backbone.options import ENDPOINTS as EP
from backbone.options import ML_ENDPOINTS as MLEP

if TYPE_CHECKING:
    from dbdie_classes.base import FullModelType


def get_extr_id(
    extr_id: int | None,
    extr_exists: bool,
) -> tuple[int]:
    return extr_id if extr_exists else (getr(f"{EP.EXTRACTOR}/count") + 1)


def goi_existing(extr_id: str):
    """Get objects info when Extractor already exist."""
    extr_info = getr(f"{EP.EXTRACTOR}/{extr_id}")

    raise NotImplementedError
    fmts_ = ...  # TODO
    extr = ...
    models = {
        fmt: getr(f"{EP.MODELS}/{mid}")
        for fmt, mid in extr_info["models_ids"].items()
    }

    return extr, models, PredictableTuples.from_fmts(fmts_)


def goi_not_existing(
    extr_id: int,
    extr_name: str,
    fmts: list["FullModelType"] | None,
    cps_id: int,
):
    """Get objects info when Extractor doesn't exist yet."""
    fmts_ = deepcopy(fmts) if fmts is not None else [
        KILLER_FMT.CHARACTER,
        SURV_FMT.CHARACTER,
        KILLER_FMT.ITEM,
        SURV_FMT.ITEM,
        KILLER_FMT.PERKS,
        SURV_FMT.PERKS,
        SURV_FMT.STATUS,
    ]

    model_count = getr(f"{EP.MODELS}/count")

    extr_info = {
        "id": extr_id,
        "name": extr_name,  # TODO: add optional randomized
        "cps_id": cps_id,
    }
    models_info = {
        fmt: {"id": model_count + i}
        for i, fmt in enumerate(fmts_)
    }

    return extr_info, models_info, PredictableTuples.from_fmts(fmts_)


def get_fmts_with_counts(ptups: PredictableTuples) -> dict["FullModelType", int]:
    return {
        ptup.fmt: getr(
            f"{EP.MT_TO_ENDPOINT[ptup.mt]}/count",
            params={"ifk": ptup.ifk},
        )
        for ptup in ptups
    }


def train_extractor(
    extr_id: int,
    extr_name: str,
    cps_name: str,
    models_ids: dict["FullModelType", int],
    fmts_with_counts: dict["FullModelType", int],
) -> tuple[dict, dict]:
    resp = postr(
        MLEP.TRAIN,
        ml=True,
        json={
            "id": extr_id,
            "name": extr_name,
            "cps_name": cps_name,
            "fmts": {
                fmt: {
                    "id": models_ids[fmt],
                    "fmt": fmt,
                    "total_classes": total_classes,
                    "cps_name": cps_name,
                    "trained_model": None,  # TODO: Probably separate TrainModel from a train API schema
                }
                for fmt, total_classes in fmts_with_counts.items()
            },
            "custom_dbdvr": None,  # TODO
        },
    )
    return resp["extractor"], resp["models"]


def set_today(extr_info, models_info):
    today = dt.date.today().strftime("%Y-%m-%d")
    extr_info["date_last_trained"] = today
    for fmt in models_info:
        models_info[fmt]["date_last_trained"] = today
    return extr_info, models_info


def update_models(
    extr_exists: bool,
    models_ids: dict,
    models_info,
) -> None:
    if extr_exists:
        for fmt_id, fmt in enumerate(ALL_FMTS_ORDERED):
            mid = models_ids[f"mid_{fmt_id}"]
            if mid is not None:
                putr(f"{EP.MODELS}/{mid}", json=models_info[fmt])
    else:
        for fmt_id, fmt in enumerate(ALL_FMTS_ORDERED):
            mid = models_ids[f"mid_{fmt_id}"]
            if mid is not None:
                postr(f"{EP.MODELS}/{mid}", json=models_info[fmt])


def update_extractor(
    extr_exists: bool,
    extr_info,
    extr_id: int,
) -> None:
    if extr_exists:
        putr(f"{EP.EXTRACTOR}/{extr_id}", json=extr_info)
    else:
        postr(f"{EP.EXTRACTOR}/{extr_id}", json=extr_info)
