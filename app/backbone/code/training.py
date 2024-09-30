"""Extra code for the '/training' endpoint."""

from copy import deepcopy
from dbdie_classes.options import KILLER_FMT
from dbdie_classes.options import SURV_FMT
from dbdie_classes.options.MODEL_TYPE import CHARACTER
from dbdie_classes.options.PLAYER_TYPE import pt_to_ifk
from typing import TYPE_CHECKING

from backbone.endpoints import poke
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from dbdie_classes.base import FullModelType, ModelType, PlayerType


def get_extr_id(
    extr_id: int | None,
    extr_exists: bool,
) -> tuple[int]:
    return extr_id if extr_exists else (poke(f"{EP.EXTRACTOR}/count") + 1)


def gei_existing(extr_id: str):
    extr_info = poke(f"{EP.EXTRACTOR}/{extr_id}")
    del extr_info["id"]

    fmts_ = ...  # TODO
    models_info = {
        fmt: poke(f"{EP.MODELS}/{mid}")
        for fmt, mid in extr_info["models_ids"].items()
    }
    for fmt in models_info:
        del models_info[fmt]["id"]

    raise NotImplementedError
    return extr_info, models_info, fmts_


def gei_not_existing(extr_name: str, fmts: list["FullModelType"] | None):
    fmts_ = deepcopy(fmts) if fmts is not None else [
        KILLER_FMT.CHARACTER,
        SURV_FMT.CHARACTER,
        KILLER_FMT.ITEM,
        SURV_FMT.ITEM,
        KILLER_FMT.PERKS,
        SURV_FMT.PERKS,
        SURV_FMT.STATUS,
    ]

    model_count = poke(f"{EP.MODELS}/count")
    fmts_ref = [
        {"id": fmt["id"], "name": fmt["name"]}
        for fmt in poke(f"{EP.FMT}", params={"limit": 300})
    ]
    fmts_ref = {fmt["name"]: fmt["id"] for fmt in fmts_ref}

    extr_info = {
        "name": extr_name,  # TODO: add optional randomized
        "user_id": 1,  # TODO
        "dbdv_min_id": 1,  # TODO
        "dbdv_max_id": None,  # TODO
        "special_mode": None,  # TODO
        "cropper_swarm_id": 1,  # TODO
        "models_ids": {f"mid_{fmts_ref[fmt]}": model_count + i for i, fmt in enumerate(fmts_)},
        "date_last_trained": None,  # placeholder
    }
    models_info = {
        fmt: {
            "name": f"{extr_name}-m{i}",  # TODO: add optional randomized
            "user_id": 1,  # TODO
            "fmt_id": fmts_ref[fmt],
            "cropper_swarm_id": 1,  # TODO
            "dbdv_min_id": 1,  # TODO
            "dbdv_max_id": None,  # TODO
            "special_mode": None,  # TODO
            "date_last_trained": None,  # placeholder
        }
        for i, fmt in enumerate(fmts_)
    }

    return extr_info, models_info, fmts_


def get_objects_info(
    extr_id: id,
    extr_name: str | None,
    extr_exists: bool,
    fmts: list["FullModelType"] | None,
) -> tuple[dict, dict["FullModelType", dict], list["FullModelType"]]:
    if extr_exists:
        assert fmts is None, "You can't choose fmts when retraining."
        return gei_existing(extr_id)
    else:
        extr_name_ = (
            deepcopy(extr_name) if extr_name is not None else "test-2"
        )  # TODO: add optional randomized
        return gei_not_existing(extr_name_, fmts)


def get_fmts_with_counts(
    fmts: list["FullModelType"],
    mts: list["ModelType"],
    pts: list["PlayerType"],
) -> dict["FullModelType", int]:
    return {
        fmt: poke(
            f"{EP.MT_TO_ENDPOINT[mt]}/count",
            params={
                ("is_killer" if mt == CHARACTER else "is_for_killer"): pt_to_ifk(pt)
            },
        )
        for fmt, mt, pt in zip(fmts, mts, pts)
    }
