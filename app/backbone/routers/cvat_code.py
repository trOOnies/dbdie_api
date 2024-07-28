import os
import datetime as dt
from shutil import move
from fastapi import APIRouter
from dbdie_ml.paths import absp, CROPPED_IMG_FD
from backbone.code.cvat_code import load_images, create_cvat_task

router = APIRouter(prefix="/cvat")

IN_CVAT_FD = "data/img/in_cvat"  # TODO: Add to ml and import

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


@router.post("/fill_cvat")
def fill_cvat(
    project_name: str,
    move_on_finish: bool,  # useful for partial uploads
):
    """Fills CVAT with crops that are pending."""
    project = PROJECTS_DICT[project_name]
    print(project_name)
    print(project)
    print("Move on finish:", move_on_finish)

    imgs, staged_images = load_images(
        project=project,
        main_images_fd=CROPPED_IMG_FD,
        dst_fd=IN_CVAT_FD,
    )
    imgs_full = [
        absp(os.path.join(f"data/crops/{project_name}", f))
        for f in imgs
    ]

    now_str = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    task_name = f"{project_name}_{now_str}"
    print("Task:", task_name)

    create_cvat_task(project, task_name, imgs_full)

    if move_on_finish:
        for f in staged_images:
            move(
                absp(os.path.join(CROPPED_IMG_FD, f"{f}.png")),
                absp(os.path.join(IN_CVAT_FD, f"{f}.png")),
            )
        print("Images moved")
