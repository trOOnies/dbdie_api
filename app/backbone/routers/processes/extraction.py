"""Endpoint for extraction related processes."""

from copy import deepcopy
from dbdie_ml.classes.base import FullModelType, PathToFolder
from dbdie_ml.ml.extractor import InfoExtractor
from dbdie_ml.options import MODEL_TYPES as MT
from fastapi import APIRouter, status
import requests

from backbone.code.extraction import get_raw_dataset, split_fmts
from backbone.endpoints import endp, parse_or_raise
from backbone.options import ENDPOINTS as EP

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_extract(
    ie_folder_path: PathToFolder,
    fmts: list[FullModelType] | None = None,
):
    """IMPORTANT. If doing partial uploads, please use 'fmts'."""
    ie = InfoExtractor.from_folder(ie_folder_path)

    try:
        fmts_ = deepcopy(fmts) if fmts is not None else ie.fmts
        mts, pts = split_fmts(fmts_)

        raw_dataset = get_raw_dataset(fmts_, mts, pts)
        preds_dict = ie.predict_batch(raw_dataset, fmts_)
    finally:
        ie.flush()
        del ie

    for i, (mid, pid) in enumerate(
        raw_dataset["match_id"].values,
        raw_dataset["player_id"].values,
    ):
        parse_or_raise(
            requests.post(
                endp(EP.LABELS),
                json={
                    "match_id": mid,
                    "player": {
                        "id": pid,
                        "character_id": preds_dict[MT.CHARACTER][i],
                        "perk_ids":     preds_dict[MT.PERKS][i],
                        "item_id":      preds_dict[MT.ITEM][i],
                        "addon_ids":    preds_dict[MT.ADDONS][i],
                        "offering_id":  preds_dict[MT.OFFERING][i],
                        "status_id":    preds_dict[MT.STATUS][i],
                        "points":       preds_dict[MT.POINTS][i],
                        "prestige":     preds_dict[MT.PRESTIGE][i],
                    },
                    "user_id": 1,  # TODO
                    "extractor_id": 1,  # TODO
                    "manually_checked": False,
                }
            ),
            exp_status_code=status.HTTP_201_CREATED,
        )
