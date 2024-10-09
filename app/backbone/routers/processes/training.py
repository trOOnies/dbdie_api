"""Endpoint for training related processes."""

from dbdie_classes.base import FullModelType
from dbdie_classes.options.FMT import from_fmts
from fastapi import APIRouter, status
import requests

from backbone.code.training import (
    get_extr_id,
    get_fmts_with_counts,
    get_objects_info,
    set_today,
    train_extractor,
    update_extractor,
    update_models,
)
from backbone.endpoints import endp, parse_or_raise

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_train(
    extr_id: int | None = None,
    extr_name: str | None = None,
    cps_id: int | None = None,
    fmts: list[FullModelType] | None = None,
):
    """IMPORTANT. If doing partial training, please use 'fmts'."""
    extractor_exists = extr_id is not None
    if extractor_exists:
        assert extr_name is None, "No name is needed if the extractor already exists."
        assert cps_id is None, "No cps_id is needed if the extractor already exists."

    extr_id_ = get_extr_id(extr_id, extractor_exists)

    extr_info, models_info, fmts_ = get_objects_info(
        extr_id_,
        extr_name,
        extractor_exists,
        fmts,
        cps_id,
    )
    mts, pts, _ = from_fmts(fmts_)

    fmts_with_counts = get_fmts_with_counts(fmts_, mts, pts)
    cps_name = parse_or_raise(
        requests.get(endp(f"/cropper-swarm/{extr_info['cropper_swarm_id']}"))
    )["name"]

    train_extractor(
        extr_info["id"],
        extr_info["name"],
        cps_name,
        {fmt: minfo["id"] for fmt, minfo in models_info.items()},
        fmts_with_counts,
    )
    extr_info, models_info = set_today(extr_info, models_info)

    update_models(extractor_exists, extr_info["models_ids"], models_info)
    update_extractor(extractor_exists, extr_info, extr_id_)
