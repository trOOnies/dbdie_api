"""Endpoint for training related processes."""

from copy import deepcopy
from dbdie_ml.classes.base import FullModelType
from dbdie_ml.ml.extractor import InfoExtractor
from fastapi import APIRouter, status

from backbone.code.extraction import get_raw_dataset, split_fmts

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_train(fmts: list[FullModelType] | None = None):
    """IMPORTANT. If doing partial training, please use 'fmts'."""
    ie = InfoExtractor("extr-default")
    ie.init_extractor(fmts)

    try:
        fmts_ = deepcopy(fmts) if fmts is not None else ie.fmts
        mts, pts = split_fmts(fmts_)

        raw_dataset = get_raw_dataset(fmts_, mts, pts)
        preds_dict = ie.train(..., ..., ...)  # TODO
    finally:
        ie.flush()
        del ie
