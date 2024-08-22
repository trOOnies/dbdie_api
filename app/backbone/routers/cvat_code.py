import os
import datetime as dt
from shutil import move
from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from dbdie_ml.paths import absp, CROPS_MAIN_FD_RP, CROPPED_IMG_FD_RP, IN_CVAT_FD_RP
from backbone.code.cvat_code import load_images, create_cvat_task

router = APIRouter()

SCREENSHOT_SL = 6
PLAYER_SL = 8
PROJECTS_DICT = {
    "perks__killer": {
        "project_id": 1,
        "suffix_len": PLAYER_SL,
    },
    "perks__surv": {
        "project_id": 2,
        "suffix_len": PLAYER_SL,
    },
    "characters__killer": {
        "project_id": 4,
        "suffix_len": PLAYER_SL,
    },
    "characters__surv": {
        "project_id": 5,
        "suffix_len": PLAYER_SL,
    },
    "status": {
        "project_id": 6,
        "suffix_len": PLAYER_SL,
    },
}


@router.post(
    "/fill-cvat",
    status_code=status.HTTP_201_CREATED,
)
def fill_cvat(
    project_name: str,
    move_on_finish: bool,  # useful for partial uploads
):
    """Fills CVAT with crops that are pending."""
    project = PROJECTS_DICT.get(project_name)
    if project is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Project '{project_name}' doesn't exist"
        )
    print(project_name)
    print(project)
    print("Move on finish:", move_on_finish)

    crops_main_fd = absp(CROPS_MAIN_FD_RP)
    cropped_img_fd = absp(CROPPED_IMG_FD_RP)
    in_cvat_fd = absp(IN_CVAT_FD_RP)

    imgs, staged_images = load_images(
        project=project,
        main_images_fd=cropped_img_fd,
        dst_fd=in_cvat_fd,
    )
    imgs_full = [os.path.join(crops_main_fd, project_name, f) for f in imgs]

    now_str = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    task_name = f"{project_name}_{now_str}"
    print("Task:", task_name)

    create_cvat_task(project, task_name, imgs_full)

    if move_on_finish:
        for f in staged_images:
            move(
                os.path.join(cropped_img_fd, f"{f}.png"),
                os.path.join(in_cvat_fd, f"{f}.png"),
            )
        print("Images moved")
