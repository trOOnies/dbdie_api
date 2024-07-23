import os
import re
import requests
from typing import Literal
from sqlalchemy import func
from dbdie_ml.schemas import Perk, Character, Addon

ENDPOINT_PATT = re.compile("[a-z]+$")
NOT_WS_PATT = re.compile(r"\S")

MODELS_DICT = {"perk": Perk, "character": Character, "addon": Addon}


def req_wrap(endpoint: str, id: int) -> dict:
    assert ENDPOINT_PATT.match(endpoint)
    resp = requests.get(f"{os.environ['HOST']}/{endpoint}/{id}")
    return resp.json()


def filter_with_text(query, search_text: str, use_model: Literal["perk", "character"]):
    if search_text != "":
        search_text = search_text.lower()
        model = MODELS_DICT[use_model]
        if use_model in {"perk", "charcater", "addon"}:
            query = query.filter(func.lower(model.name).contains(search_text))
        else:
            raise NotImplementedError
    return query
