from functools import partial
from os import listdir, mkdir
from os.path import exists, isdir, join
from shutil import copy, move
from typing import TYPE_CHECKING

from dbdie_classes.paths import (
    CROPS_MAIN_FD_RP,
    CROPS_VERSIONS_FD_RP,
    IMG_MAIN_FD_RP,
    IMG_VERSIONS_FD_RP,
    LABELS_FD_RP,
    LABELS_MAIN_FD_RP,
    LABELS_REF_FD_RP,
    LABELS_VERSIONS_FD_RP,
    OLD_VS,
    absp,
)

if TYPE_CHECKING:
    from dbdie_classes.base import PathToFolder

IMG_VERSIONS_FD = absp(IMG_VERSIONS_FD_RP)
LABELS_VERSIONS_FD = absp(LABELS_VERSIONS_FD_RP)


def get_new_version_id() -> int:
    versions = listdir(absp(CROPS_VERSIONS_FD_RP))
    return max(int(fd) for fd in versions) + 1 if versions else 0


def process_version(main_fd: "PathToFolder", version_id: int) -> "PathToFolder":
    """Generic function for asserting that a version doesn't already exist,
    and creating its directory if False.
    """
    version_fd = join(main_fd, str(version_id))
    assert not exists(version_fd)
    mkdir(version_fd)
    return version_fd


def backup_crops(version_id: int) -> None:
    """Backup DBDIE active crops."""
    version_fd = process_version(absp(CROPS_VERSIONS_FD_RP), version_id)

    crops_main_fd = absp(CROPS_MAIN_FD_RP)

    all_dsts = [
        fd
        for fd in listdir(crops_main_fd)
        if (not fd.startswith("_")) and isdir(join(crops_main_fd, fd))
    ]

    for dst in all_dsts:
        from_path = join(crops_main_fd, dst)
        if not exists(from_path):
            continue
        move(from_path, join(version_fd, dst))

    for dst in all_dsts:
        mkdir(join(crops_main_fd, dst))

    copy(
        join(crops_main_fd, "crop_settings.py"),
        join(version_fd, "crop_settings.py"),
    )


def backup_images(version_id: int) -> None:
    """Backup DBDIE active images."""
    img_main_fd = absp(IMG_MAIN_FD_RP)

    version_fd = process_version(IMG_VERSIONS_FD, version_id)
    img_fds = [fd for fd in listdir(img_main_fd) if fd != OLD_VS]
    for fd in img_fds:
        src_fd = join(img_main_fd, fd)
        dst_fd = join(version_fd, fd)
        move(src_fd, dst_fd)
        mkdir(src_fd)


def backup_labels(version_id: int) -> None:
    """Backup DBDIE active labels."""
    version_fd = process_version(LABELS_VERSIONS_FD, version_id)
    rp = partial(join, version_fd)

    labels_main_fd = absp(LABELS_MAIN_FD_RP)
    labels_fd = absp(LABELS_FD_RP)
    labels_ref_fd = absp(LABELS_REF_FD_RP)

    move(labels_fd, rp("labels"))
    move(labels_ref_fd, rp("label_ref"))

    label_fds = [fd for fd in listdir(labels_main_fd) if fd.startswith("project_")]
    for fd in label_fds:
        move(join(labels_main_fd, fd), rp(fd))

    mkdir(labels_fd)
    mkdir(labels_ref_fd)
