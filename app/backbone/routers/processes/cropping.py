"""Endpoint for cropping related purposes."""

from fastapi import APIRouter, status
import requests

from backbone.endpoints import parse_or_raise
from backbone.options import ML_ENDPOINTS as MLEP

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_crop(
    move: bool = True,
    use_croppers: list[str] | None = None,
    use_fmts: list[str] | None = None,
):
    """[NEW] Run all Croppers iterating on images first.

    move: Whether to move the source images at the end of the cropping.
        Note: The MovableReport still avoid creating crops
        of duplicate source images.

    Filter options (cannot be used at the same time):
    - use_croppers: Filter cropping using Cropper names (level=Cropper).
    - use_fmt: Filter cropping using FullModelTypes names (level=crop type).
    """
    return parse_or_raise(
        requests.post(
            MLEP.CROP,
            json={
                "move": move,
                "use_croppers": use_croppers,
                "use_fmts": use_fmts,
            },
        )
    )
