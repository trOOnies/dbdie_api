import re
import requests
from typing import Literal
from sqlalchemy import func
from dbdie_ml.schemas.predictables import Perk, Character, Addon
from dbdie_ml.schemas.groupings import MatchOut
from backbone.config import endp

ENDPOINT_PATT = re.compile("[a-z]+$")
NOT_WS_PATT = re.compile(r"\S")

ModelAllowed = Literal["perk", "character", "addon", "match"]
MODELS_DICT = {"perk": Perk, "character": Character, "addon": Addon, "match": MatchOut}


def req_wrap(endpoint: str, id: int) -> dict:
    """Request wrapper for a GET request for a type 'endpoint' with an id 'id'."""
    assert ENDPOINT_PATT.match(endpoint)
    resp = requests.get(endp(f"/{endpoint}/{id}"))
    return resp.json()


def filter_with_text(query, search_text: str, use_model: ModelAllowed):
    if search_text != "":
        search_text = search_text.lower()
        model = MODELS_DICT[use_model]
        if use_model in {"perk", "character", "addon"}:
            query = query.filter(func.lower(model.name).contains(search_text))
        elif use_model == "match":
            query = query.filter(func.lower(model.filename).contains(search_text))
        else:
            raise NotImplementedError
    return query
