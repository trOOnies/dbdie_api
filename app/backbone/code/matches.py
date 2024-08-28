from typing import TYPE_CHECKING

import requests
from backbone.config import endp
from dbdie_ml.classes.version import DBDVersion
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from dbdie_ml.schemas.groupings import MatchCreate


def form_match(match: "MatchCreate") -> dict:
    new_match = {"id": requests.get(endp("/matches/count")).json()} | match.model_dump()

    if new_match["dbd_version"] is None:
        new_match["dbd_version_id"] = None
    else:
        dbdv = str(DBDVersion(**new_match["dbd_version"]))
        payload = {"dbd_version_str": dbdv}

        resp = requests.get(endp("/dbd-version/id"), params=payload)
        if resp.status_code != status.HTTP_200_OK:
            raise HTTPException(resp.status_code, resp.json()["detail"])

        new_match["dbd_version_id"] = resp.json()

    del new_match["dbd_version"]
    return new_match
