import os
from typing import TYPE_CHECKING
from tqdm import tqdm
from cvat_sdk import make_client
from cvat_sdk.core.progress import ProgressReporter
from cvat_sdk.core.proxies.tasks import ResourceType

if TYPE_CHECKING:
    from dbdie_ml.classes import PathToFolder, Filename


class NewProgressReporter(ProgressReporter):
    def __init__(self) -> None:
        super().__init__()
        self.pbar = None

    def report_status(self, progress: int):
        """Updates the progress bar"""
        print(self.pbar.__n)

    def advance(self, delta: int):
        """Updates the progress bar"""
        self.pbar.update(delta)

    def start2(
        self,
        total: int,
        *,
        desc: str | None = None,
        unit: str = "it",
        unit_scale: bool = False,
        unit_divisor: int = 1000,
        **kwargs,
    ) -> None:
        """
        Initializes the progress bar.

        total, desc, unit, unit_scale, unit_divisor have the same meaning as in tqdm.

        kwargs is included for future extension; implementations of this method
        must ignore it.
        """
        self.pbar = tqdm(total=total, desc=desc)

    def finish(self):
        """Finishes the progress bar"""
        self.pbar.close()


def load_images(
    project: dict, main_images_fd: "PathToFolder", dst_fd: "PathToFolder"
) -> tuple[list["Filename"], set["Filename"]]:
    staged_images = set(f[:-4] for f in os.listdir(main_images_fd))
    assert staged_images
    print("STAGED IMAGES:", len(staged_images))

    dst_images = set(f[:-4] for f in os.listdir(dst_fd))
    assert all(f not in dst_images for f in staged_images)

    imgs = [
        f
        for f in os.listdir(project["img_folder"])
        if f[: -project["suffix_len"]] in staged_images
    ]
    assert imgs
    print("CROPS TO UPLOAD:", len(imgs))

    staged_images = set(
        f for f in staged_images if f in set(i[: -project["suffix_len"]] for i in imgs)
    )

    return imgs, staged_images


def create_cvat_task(
    project,
    task_name,
    imgs_full,
) -> None:
    with make_client(
        host=os.environ["CVAT_HOST"],
        credentials=(os.environ["CVAT_MAIL"], os.environ["CVAT_PASSWORD"]),
    ) as client:
        task_spec = {"project_id": project["project_id"], "name": task_name}

        r = NewProgressReporter()
        client.tasks.create_from_data(
            spec=task_spec,
            resource_type=ResourceType.LOCAL,
            resources=imgs_full,
            pbar=r,
        )
