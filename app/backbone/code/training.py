"""Extra code for the '/training' endpoint."""

from copy import deepcopy
import datetime as dt
from dbdie_classes.options import KILLER_FMT
from dbdie_classes.options import SURV_FMT
from dbdie_classes.options.MODEL_TYPE import CHARACTER
from dbdie_classes.options.PLAYER_TYPE import pt_to_ifk
import requests
from typing import TYPE_CHECKING

from backbone.endpoints import endp, mlendp, parse_or_raise, poke
from backbone.options import ENDPOINTS as EP
from backbone.options import ML_ENDPOINTS as MLEP

if TYPE_CHECKING:
    from dbdie_classes.base import FullModelType, ModelType, PlayerType


def get_extr_id(
    extr_id: int | None,
    extr_exists: bool,
) -> tuple[int]:
    return extr_id if extr_exists else (poke(f"{EP.EXTRACTOR}/count") + 1)


def gei_existing(extr_id: str):
    extr_info = poke(f"{EP.EXTRACTOR}/{extr_id}")

    fmts_ = ...  # TODO
    models_info = {
        fmt: poke(f"{EP.MODELS}/{mid}")
        for fmt, mid in extr_info["models_ids"].items()
    }

    raise NotImplementedError
    return extr_info, models_info, fmts_


def gei_not_existing(
    extr_id: int,
    extr_name: str,
    fmts: list["FullModelType"] | None,
):
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
        for fmt in poke(EP.FMT, params={"limit": 300})
    ]
    fmts_ref = {fmt["name"]: fmt["id"] for fmt in fmts_ref}
    models_ids = [model_count + i for i in range(len(fmts_))]

    extr_info = {
        "id": extr_id,
        "name": extr_name,  # TODO: add optional randomized
        "user_id": 1,  # TODO
        "dbdv_min_id": 1,  # TODO
        "dbdv_max_id": None,  # TODO
        "special_mode": None,  # TODO
        "cropper_swarm_id": 1,  # TODO
        "models_ids": {
            f"mid_{fmts_ref[fmt]}": mid
            for fmt, mid in zip(fmts_, models_ids)
        },
        "date_last_trained": None,  # placeholder
    }
    models_info = {
        fmt: {
            "id": mid,
            "name": f"{extr_name}-m{i}",  # TODO: add optional randomized
            "user_id": 1,  # TODO
            "fmt_id": fmts_ref[fmt],
            "cropper_swarm_id": 1,  # TODO
            "dbdv_min_id": 1,  # TODO
            "dbdv_max_id": None,  # TODO
            "special_mode": None,  # TODO
            "date_last_trained": None,  # placeholder
        }
        for i, (fmt, mid) in enumerate(zip(fmts_, models_ids))
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
        return gei_not_existing(extr_id, extr_name_, fmts)


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


def train_extractor(
    extr_id: int,
    extr_name: str,
    models_ids: dict["FullModelType", int],
    fmts_with_counts: dict["FullModelType", int],
) -> None:
    parse_or_raise(
        requests.post(
            mlendp(f"{MLEP.TRAIN}/batch"),
            json={
                "id": extr_id,
                "name": extr_name,
                "full_model_types": {
                    fmt: {
                        "model_id": models_ids[fmt],
                        "total_classes": total_classes,
                    }
                    for fmt, total_classes in fmts_with_counts.items()
                },
            },
        ),
        exp_status_code=201,  # Created
    )


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
        for mid, mjson in zip(models_ids.values(), models_info.values()):
            parse_or_raise(
                requests.put(
                    endp(f"{EP.MODELS}/{mid}"),
                    json=mjson,
                ),
            )
    else:
        for mid, mjson in zip(models_ids.values(), models_info.values()):
            parse_or_raise(
                requests.post(
                    endp(f"{EP.MODELS}/{mid}"),
                    json=mjson,
                ),
            )


def update_extractor(
    extr_exists: bool,
    extr_info,
    extr_id: int,
) -> None:
    if extr_exists:
        parse_or_raise(
            requests.put(
                endp(f"{EP.EXTRACTOR}/{extr_id}"),
                json=extr_info,
            ),
        )
    else:
        parse_or_raise(
            requests.post(
                endp(f"{EP.EXTRACTOR}/{extr_id}"),
                json=extr_info,
            ),
        )
