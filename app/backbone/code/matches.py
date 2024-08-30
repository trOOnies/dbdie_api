from typing import TYPE_CHECKING

import requests
from backbone.endpoints import dbd_version_str_to_id, endp
from dbdie_ml.classes.version import DBDVersion

if TYPE_CHECKING:
    from dbdie_ml.schemas.groupings import MatchCreate


def form_match(match: "MatchCreate") -> dict:
    new_match = {"id": requests.get(endp("/matches/count")).json()} | match.model_dump()

    if new_match["dbd_version"] is None:
        new_match["dbd_version_id"] = None
    else:
        dbdv = str(DBDVersion(**new_match["dbd_version"]))

        new_match["dbd_version_id"] = dbd_version_str_to_id(dbdv)

    del new_match["dbd_version"]
    return new_match
