import re
from typing import Literal

import requests
from backbone.config import endp
from backbone.exceptions import ItemNotFoundException
from dbdie_ml.schemas.groupings import MatchOut
from dbdie_ml.schemas.predictables import AddonOut, CharacterOut, PerkOut
from sqlalchemy import func

ENDPOINT_PATT = re.compile("[a-z]+$")
NOT_WS_PATT = re.compile(r"\S")

ModelAllowed = Literal["perk", "character", "addon", "match"]
SCHEMAS_DICT = {
    "perk": PerkOut,
    "character": CharacterOut,
    "addon": AddonOut,
    "match": MatchOut,
}


def get_req(endpoint: str, id: int) -> dict:
    """Request wrapper for a GET request for a type 'endpoint' with an id 'id'."""
    assert ENDPOINT_PATT.match(endpoint)
    resp = requests.get(endp(f"/{endpoint}/{id}"))
    if resp.status_code != 200:
        raise ItemNotFoundException(endpoint.capitalize()[:-1], id)
    return resp.json()


def filter_with_text(query, search_text: str, use_model: ModelAllowed):
    if search_text != "":
        search_text = search_text.lower()
        model = SCHEMAS_DICT[use_model]
        if use_model in {"perk", "character", "addon"}:
            query = query.filter(func.lower(model.name).contains(search_text))
        elif use_model == "match":
            query = query.filter(func.lower(model.filename).contains(search_text))
        else:
            raise NotImplementedError
    return query
