"""Endpoint for training related processes."""

from copy import deepcopy
from dbdie_classes.base import FullModelType
from dbdie_classes.options import MODEL_TYPES as MT
from dbdie_classes.options import PLAYER_TYPE as PT
from fastapi import APIRouter, status
import requests

from backbone.endpoints import endp, parse_or_raise
from backbone.options import ENDPOINTS as EP
from backbone.options import ML_ENDPOINTS as MLEP

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_train(
    fmts: list[FullModelType] | None = None,
    extr_id: int | None = None,
):
    """IMPORTANT. If doing partial training, please use 'fmts'."""
    extractor_exists = extr_id is not None
    extr_id_ = (
        extr_id if extractor_exists
        else parse_or_raise(
            requests.get(f"{EP.EXTRACTOR}/count")
        )
    )

    if extractor_exists:
        assert fmts is None, "You can't choose fmts when retraining"

    if extractor_exists:
        extr_info = parse_or_raise(
            requests.get(f"{EP.EXTRACTOR}/{extr_id_}")
        )
        fmts_ = ...
    else:
        fmts_ = deepcopy(fmts) if fmts is not None else [
            f"{MT.CHARACTER}__{PT.KILLER}",
            f"{MT.CHARACTER}__{PT.SURV}",
            f"{MT.ITEM}__{PT.KILLER}",
            f"{MT.ITEM}__{PT.SURV}",
            f"{MT.PERKS}__{PT.KILLER}",
            f"{MT.PERKS}__{PT.SURV}",
            f"{MT.STATUS}__{PT.SURV}",
        ]

    extr_name = extr_info["name"] if extractor_exists else "random-name"  # TODO
    mts, pts = PT.extract_mts_and_pts(fmts_)

    fmts_with_counts = {
        fmt: parse_or_raise(
            requests.get(
                endp(f"{EP.MT_TO_ENDPOINT[mt]}/count"),
                params={
                    ("is_killer" if mt == MT.CHARACTER else "is_for_killer"): PT.pt_to_ifk(pt)
                },
            )
        )
        for fmt, mt, pt in zip(fmts_, mts, pts)
    }

    parse_or_raise(
        requests.post(
            f"{MLEP.TRAIN}/batch",
            json={
                "extr_name": extr_name,
                "fmts_with_counts": fmts_with_counts,
            },
        ),
        exp_status_code=status.HTTP_201_CREATED,
    )

    # TODO: Update extractor and models last train date
    if extractor_exists:
        parse_or_raise(
            requests.post(
                f"{EP.MODEL}/{extr_id_}",
                json={...},
            ),
            exp_status_code=status.HTTP_201_CREATED,
        )
    else:
        parse_or_raise(
            requests.put(
                f"{EP.MODEL}/{extr_id_}",
                json={...},
            ),
        )
