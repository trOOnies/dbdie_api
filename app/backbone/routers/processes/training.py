"""Endpoint for training related processes."""

import datetime as dt
from dbdie_classes.base import FullModelType
from dbdie_classes.options.FMT import from_fmts
from fastapi import APIRouter, status
import requests

from backbone.code.training import get_extr_id, get_fmts_with_counts, get_objects_info
from backbone.endpoints import endp, mlendp, parse_or_raise
from backbone.options import ENDPOINTS as EP
from backbone.options import ML_ENDPOINTS as MLEP

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_train(
    name: str | None = None,
    fmts: list[FullModelType] | None = None,
    extr_id: int | None = None,
):
    """IMPORTANT. If doing partial training, please use 'fmts'."""
    extractor_exists = extr_id is not None
    if extractor_exists:
        assert name is None, "No name is needed if the extractor already exists."

    extr_id_ = get_extr_id(extr_id, extractor_exists)

    extr_info, models_info, fmts_ = get_objects_info(extr_id_, name, extractor_exists, fmts)
    mts, pts, _ = from_fmts(fmts_)

    fmts_with_counts = get_fmts_with_counts(fmts_, mts, pts)

    # Train extractor
    parse_or_raise(
        requests.post(
            mlendp(f"{MLEP.TRAIN}/batch"),
            params={"extr_name": extr_info["name"]},
            json=fmts_with_counts,
        ),
        exp_status_code=status.HTTP_201_CREATED,
    )

    today = dt.date.today().strftime("%Y-%m-%d")
    extr_info["date_last_trained"] = today
    for fmt in models_info:
        models_info[fmt]["date_last_trained"] = today

    # Update models
    if extractor_exists:
        for mid, mjson in zip(extr_info["models_ids"].values(), models_info.values()):
            parse_or_raise(
                requests.put(
                    endp(f"{EP.MODELS}/{mid}"),
                    json=mjson,
                ),
            )
    else:
        for mid, mjson in zip(extr_info["models_ids"].values(), models_info.values()):
            parse_or_raise(
                requests.post(
                    endp(f"{EP.MODELS}/{mid}"),
                    json=mjson,
                ),
            )

    # Update extractor
    if extractor_exists:
        parse_or_raise(
            requests.put(
                endp(f"{EP.EXTRACTOR}/{extr_id_}"),
                json=extr_info,
            ),
        )
    else:
        parse_or_raise(
            requests.post(
                endp(f"{EP.EXTRACTOR}/{extr_id_}"),
                json=extr_info,
            ),
        )
