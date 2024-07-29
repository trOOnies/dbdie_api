import os
from typing import TYPE_CHECKING
from functools import partial
from shutil import move, copy
from dbdie_ml.paths import absp
if TYPE_CHECKING:
    from dbdie_ml.classes import PathToFolder

OLD_VERSIONS_NAME = "_old_versions"

CROPS_MAIN_FD = absp("data/crops")
CROPS_VERSIONS_FD = os.path.join(CROPS_MAIN_FD, OLD_VERSIONS_NAME)

IMG_MAIN_FD = absp("data/img")
IMG_VERSIONS_FD = os.path.join(IMG_MAIN_FD, OLD_VERSIONS_NAME)

LABELS_MAIN_FD = absp("data/labels")
LABELS_VERSIONS_FD = os.path.join(LABELS_MAIN_FD, OLD_VERSIONS_NAME)
LABELS_FD = os.path.join(LABELS_MAIN_FD, "labels")
LABELS_REF_FD = os.path.join(LABELS_MAIN_FD, "label_ref")


def get_new_version_id() -> int:
    versions = os.listdir(CROPS_VERSIONS_FD)
    return max(int(fd) for fd in versions) + 1 if versions else 0


def process_version(main_fd: "PathToFolder", version_id: int) -> "PathToFolder":
    """Generic function for asserting that a version doesn't already exist,
    and creating its directory if False.
    """
    version_fd = os.path.join(main_fd, str(version_id))
    assert not os.path.exists(version_fd)
    os.mkdir(version_fd)
    return version_fd


def backup_crops(version_id: int) -> None:
    """Backup DBDIE active crops."""
    version_fd = process_version(CROPS_VERSIONS_FD, version_id)

    all_dsts = [
        fd
        for fd in os.listdir(CROPS_MAIN_FD)
        if (not fd.startswith("_")) and os.path.isdir(os.path.join(CROPS_MAIN_FD, fd))
    ]

    for dst in all_dsts:
        from_path = os.path.join(CROPS_MAIN_FD, dst)
        if not os.path.exists(from_path):
            continue
        move(from_path, os.path.join(version_fd, dst))

    for dst in all_dsts:
        os.mkdir(os.path.join(CROPS_MAIN_FD, dst))

    copy(
        os.path.join(CROPS_MAIN_FD, "crop_settings.py"),
        os.path.join(version_fd, "crop_settings.py"),
    )


def backup_images(version_id: int) -> None:
    """Backup DBDIE active images."""
    version_fd = process_version(IMG_VERSIONS_FD, version_id)
    img_fds = [fd for fd in os.listdir(IMG_MAIN_FD) if fd != OLD_VERSIONS_NAME]
    for fd in img_fds:
        src_fd = os.path.join(IMG_MAIN_FD, fd)
        dst_fd = os.path.join(version_fd, fd)
        move(src_fd, dst_fd)
        os.mkdir(src_fd)


def backup_labels(version_id: int) -> None:
    """Backup DBDIE active labels."""
    version_fd = process_version(LABELS_VERSIONS_FD, version_id)
    rp = partial(os.path.join, version_fd)

    move(LABELS_FD, rp("labels"))
    move(LABELS_REF_FD, rp("label_ref"))

    label_fds = [fd for fd in os.listdir(LABELS_MAIN_FD) if fd.startswith("project_")]
    for fd in label_fds:
        move(os.path.join(LABELS_MAIN_FD, fd), rp(fd))

    os.mkdir(LABELS_FD)
    os.mkdir(LABELS_REF_FD)
