"""Extra code for /extract endpoint."""

from fastapi import status
from fastapi.exceptions import HTTPException

from backbone.endpoints import getr
from backbone.options import ENDPOINTS as EP


def get_extr_id(extr_name: str) -> int:
    """Get extractor id."""
    try:
        extr_id = getr(f"{EP.EXTRACTOR}/id", params={"extr_name": extr_name})
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extractor '{extr_name}' was not found",
            ) from e
    return extr_id


def get_zip(d: dict):
    """Get zip for prediction iteration."""
    item_ids = (
        d["item_ids"] if d["item_ids"] is not None
        else len(d["match_ids"]) * [None]
    )
    return zip(d["match_ids"], d["player_ids"], item_ids, d["preds"])
