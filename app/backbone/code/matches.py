"""Extra code for the '/matches' endpoint."""

import os
import re
import shutil
from typing import TYPE_CHECKING

from dbdie_classes.paths import absp, IMG_MAIN_FD_RP

from backbone.endpoints import getr, postr
from backbone.options import ENDPOINTS as EP

if TYPE_CHECKING:
    from dbdie_classes.base import Filename, PathToFolder
    from dbdie_classes.schemas.groupings import MatchCreate, MatchOut

DATE_PATT = re.compile(r"20\d\d-[0-1]\d-[0-3]\d")


def form_match(match: "MatchCreate") -> dict:
    new_match = {"id": getr(f"{EP.MATCHES}/count")} | match.model_dump()
    return new_match


def get_versioned_fd_data(
    dbdv_name: str,
) -> tuple[list["Filename"], "PathToFolder", "PathToFolder"]:
    """Get necessary objects for a certain DBDVersionOut."""
    src_main_fd = absp(IMG_MAIN_FD_RP)

    src_fd = os.path.join(src_main_fd, f"versioned/{dbdv_name}")
    assert os.path.isdir(src_fd)
    fs = os.listdir(src_fd)
    assert fs, "Versioned folder cannot be empty."

    dst_fd = os.path.join(src_main_fd, "pending")

    return fs, src_fd, dst_fd


def upload_dbdv_matches(
    filenames: list["Filename"],
    src_fd: "PathToFolder",
    dst_fd: "PathToFolder",
    dbdv_id: int,
    special_mode: bool | None,
) -> list["MatchOut"]:
    """Upload loop for matches of a certain DBDVersionOut."""
    matches = []
    dates = [DATE_PATT.search(f).group() for f in filenames]

    for f, d in zip(filenames, dates):
        matches.append(
            postr(
                EP.MATCHES,
                json={
                    "filename": f,
                    "match_date": d,
                    "dbdv_id": dbdv_id,
                    "special_mode": special_mode,
                    "user_id": 1,  # TODO
                    "extr_id": None,  # TODO
                    "kills": None,  # TODO
                },
            )
        )
        shutil.move(os.path.join(src_fd, f), os.path.join(dst_fd, f))

    return matches
