"""Endpoint for training related processes."""

from copy import deepcopy
from dbdie_classes.base import FullModelType
from fastapi import APIRouter, status

from backbone.code.training import (
    get_extr_id,
    get_fmts_with_counts,
    goi_existing,
    goi_not_existing,
    set_today,
    train_extractor,
    update_extractor,
    update_models,
)
from backbone.endpoints import EP, getr

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def batch_train(
    extr_id: int | None = None,
    extr_name: str | None = None,
    cps_id: int | None = None,
    fmts: list[FullModelType] | None = None,
):
    """IMPORTANT. If doing partial training, please use 'fmts'."""
    extr_exists = extr_id is not None
    if extr_exists:
        assert extr_name is None, "No name is needed if the extractor already exists."
        assert cps_id is None,  "No cps_id is needed if the extractor already exists."

    extr_id_ = get_extr_id(extr_id, extr_exists)

    if extr_exists:
        assert fmts is None, "You can't choose fmts when retraining."
        extr_info, models_info, ptups = goi_existing(extr_id_)
    else:
        extr_name_ = (
            deepcopy(extr_name) if extr_name is not None else "test-2"
        )  # TODO: add optional randomized
        extr_info, models_info, ptups = goi_not_existing(extr_id_, extr_name_, fmts, cps_id)

    fmts_with_counts = get_fmts_with_counts(ptups)
    cps_name = getr(f"{EP.CROPPER_SWARM}/{extr_info['cps_id']}")["name"]

    extr_out, models_out = train_extractor(
        extr_info["id"],
        extr_info["name"],
        cps_name,
        models_ids={fmt: minfo["id"] for fmt, minfo in models_info.items()},
        fmts_with_counts=fmts_with_counts,
    )

    extr_out = extr_info if extr_exists else (extr_out | extr_info)
    models_out = (
        models_info
        if extr_exists
        else {fmt: (models_out[fmt] | models_info[fmt]) for fmt in models_out}
    )

    extr_out, models_out = set_today(extr_out, models_out)

    update_models(extr_exists, extr_out["models_ids"], models_out)
    update_extractor(extr_exists, extr_out, extr_id_)
