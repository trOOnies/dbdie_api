"""Endpoint for extraction related processes."""

from dbdie_classes.base import FullModelType, PathToFolder
from dbdie_classes.options import MODEL_TYPE as MT
from fastapi import APIRouter, status
import requests

from backbone.endpoints import endp, parse_or_raise
from backbone.options import ENDPOINTS as EP
from backbone.options import ML_ENDPOINTS as MLEP

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_extract(
    ie_folder_path: PathToFolder,
    fmts: list[FullModelType] | None = None,
):
    """IMPORTANT. If doing partial uploads, please use 'fmts'."""
    resp = parse_or_raise(
        requests.post(
            f"{MLEP.EXTRACT}/batch",
            json={
                "ie_folder_path": ie_folder_path,
                "fmts": fmts,
            },
        )
    )

    preds_dict = resp["preds_dict"]
    for i, (mid, pid) in enumerate(resp["match_ids"], resp["player_ids"]):
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
