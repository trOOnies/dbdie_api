from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from dbdie_ml.cropper_swarm import CropperSwarm

router = APIRouter(prefix="/crop")

cps = CropperSwarm.from_types([["surv", "killer"], ["surv_player", "killer_player"]])


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_crop():
    try:
        cps.run()
    except AssertionError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
    return status.HTTP_201_CREATED
