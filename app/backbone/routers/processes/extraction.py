"""Endpoint for extraction related processes."""

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
import requests

from backbone.endpoints import endp, getr, postr
from backbone.options import ENDPOINTS as EP
from backbone.options import ML_ENDPOINTS as MLEP

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def batch_extract(
    extr_name: str,
    # fmts: list[FullModelType] | None = None,  # TODO
):
    """IMPORTANT. If doing partial uploads, please use 'fmts'."""
    try:
        extr_id = getr(f"{EP.EXTRACTOR}/id", params={"extr_name": extr_name})
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extractor '{extr_name}' was not found",
            ) from e

    resp = postr(
        f"{MLEP.EXTRACT}/batch",
        ml=True,
        params={
            "extr_name": extr_name,
            # "fmts": fmts,
        },
    )

    for fmt, d in resp.items():
        for mid, pid, pred in zip(d["match_ids"], d["player_ids"], d["preds"]):
            print({
                    "match_id": mid,
                    "player_id": pid,
                    "fmt": fmt,
                    "value": pred,
                    "user_id": 1,  # TODO
                    "extr_id": extr_id,
                })
            resp = requests.put(
                endp(f"{EP.LABELS}/predictable/strict"),
                params={
                    "match_id": mid,
                    "player_id": pid,
                    "fmt": fmt,
                    "value": pred,
                    "user_id": 1,  # TODO
                    "extr_id": extr_id,
                },
            )
            assert resp.status_code == status.HTTP_200_OK
