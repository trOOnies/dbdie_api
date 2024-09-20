"""Endpoint for training related processes."""

from copy import deepcopy
from dbdie_ml.classes.base import FullModelType
from dbdie_ml.ml.extractor import InfoExtractor
from dbdie_ml.options import MODEL_TYPES as MT
from dbdie_ml.options import PLAYER_TYPE as PT
from fastapi import APIRouter, status
import requests

from backbone.code.extraction import get_raw_dataset
from backbone.endpoints import endp, parse_or_raise
from backbone.options.ENDPOINTS import MT_TO_ENDPOINT

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_train(fmts: list[FullModelType] | None = None):
    """IMPORTANT. If doing partial training, please use 'fmts'."""
    fmts_ = deepcopy(fmts) if fmts is not None else [
        f"{MT.CHARACTER}__{PT.KILLER}",
        f"{MT.CHARACTER}__{PT.SURV}",
        f"{MT.ITEM}__{PT.KILLER}",
        f"{MT.ITEM}__{PT.SURV}",
        f"{MT.PERKS}__{PT.KILLER}",
        f"{MT.PERKS}__{PT.SURV}",
        f"{MT.STATUS}__{PT.SURV}",
    ]
    mts, pts = PT.extract_mts_and_pts(fmts_)

    fmts_with_counts = {
        fmt: parse_or_raise(
            requests.get(
                endp(f"{MT_TO_ENDPOINT[mt]}/count"),
                params={
                    ("is_killer" if mt == MT.CHARACTER else "is_for_killer"): PT.pt_to_ifk(pt)
                },
            )
        )
        for fmt, mt, pt in zip(fmts_, mts, pts)
    }

    ie = InfoExtractor("extr-default")
    ie.init_extractor(fmts_with_counts)

    try:
        raw_dataset = get_raw_dataset(fmts_, mts, pts)
        preds_dict = ie.train(..., ..., ...)  # TODO
    finally:
        ie.flush()
        del ie
