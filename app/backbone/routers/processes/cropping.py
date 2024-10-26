"""Endpoint for cropping related purposes."""

from fastapi import APIRouter, status

from dbdie_classes.base import FullModelType

from backbone.endpoints import postr
from backbone.options import ML_ENDPOINTS as MLEP

router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_crop(
    cropper_swarm_name: str,
    move: bool = True,
    use_croppers: list[str] | None = None,
    use_fmts: list[FullModelType] | None = None,
):
    """[NEW] Run all Croppers iterating on images first.

    move: Whether to move the source images at the end of the cropping.
        Note: The MovableReport still avoids creating crops
        of duplicate source images.

    Filter options (cannot be used at the same time):
    - use_croppers: Filter cropping using Cropper names (level=Cropper).
    - use_fmt: Filter cropping using FullModelTypes names (level=crop type).
    """
    return postr(
        f"{MLEP.CROP}/batch",
        ml=True,
        params={
            "cropper_swarm_name": cropper_swarm_name,
            "move": move,
        },
        json={
            "use_croppers": use_croppers,
            "use_fmts": use_fmts,
        },
    )
