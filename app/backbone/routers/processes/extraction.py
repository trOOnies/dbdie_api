"""Endpoint for extraction related processes."""

from fastapi import APIRouter, status
import requests

from backbone.code.extract import get_extr_id, get_zip
from backbone.endpoints import endp, postr
from backbone.options import ENDPOINTS as EP
from backbone.options import ML_ENDPOINTS as MLEP

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def batch_extract(
    extr_name: str,
    use_dbdvr: bool = True,
    # fmts: list[FullModelType] | None = None,  # TODO
):
    """IMPORTANT. If doing partial uploads, please use 'fmts'."""
    extr_id = get_extr_id(extr_name)
    resp = postr(
        f"{MLEP.EXTRACT}/batch",
        ml=True,
        params={
            "extr_name": extr_name,
            "use_dbdvr": use_dbdvr,
            # "fmts": fmts,
        },
    )

    put_endp = endp(f"{EP.LABELS}/predictable/strict")
    for fmt, d in resp.items():
        zipped = get_zip(d)
        for mid, pid, iid, pred in zipped:
            resp = requests.put(
                put_endp,
                params={
                    "match_id": mid,
                    "player_id": pid,
                    "item_id": iid,
                    "fmt": fmt,
                    "value": pred,
                    "user_id": 1,  # TODO
                    "extr_id": extr_id,
                },
            )
            assert resp.status_code == status.HTTP_200_OK
