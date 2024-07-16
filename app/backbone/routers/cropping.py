from typing import Literal
from fastapi import APIRouter, status

from dbdie_ml.cropper import Cropper

router = APIRouter(prefix="/crop")


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_crop(
    t: Literal["surv", "killer", "surv_player", "killer_player"]
):
    cropper = Cropper.from_type(t)
    cropper.run_crop(
        crop_only=...,
        offset=...,
        use_starting_match=...
    )
