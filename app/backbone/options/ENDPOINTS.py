"""DBDIE API high-level endpoints."""

from dbdie_classes.options import MODEL_TYPE as MT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dbdie_classes.base import Endpoint, ModelType

ADDONS      : "Endpoint" = "/addons"
CHARACTER   : "Endpoint" = "/character"
ITEM        : "Endpoint" = "/item"
OFFERING    : "Endpoint" = "/offering"
PERKS       : "Endpoint" = "/perks"
POINTS      : "Endpoint" = "/points"
PRESTIGE    : "Endpoint" = "/prestige"
STATUS      : "Endpoint" = "/status"
RARITY      : "Endpoint" = "/rarity"

# Groupings
DBD_VERSION : "Endpoint" = "/dbd-version"
MATCHES     : "Endpoint" = "/matches"
PLAYERS     : "Endpoint" = "/players"
LABELS      : "Endpoint" = "/labels"

# DBDIE objects
EXTRACTOR   : "Endpoint" = "/extractor"
MODELS      : "Endpoint" = "/models"

# Processes
CROP        : "Endpoint" = "/crop"
EXTRACT     : "Endpoint" = "/extract"
BACKUP      : "Endpoint" = "/backup"
TRAIN       : "Endpoint" = "/train"

MT_TO_ENDPOINT: dict["ModelType", "Endpoint"] = {
    MT.ADDONS: ADDONS,
    MT.CHARACTER: CHARACTER,
    MT.ITEM: ITEM,
    MT.OFFERING: OFFERING,
    MT.PERKS: PERKS,
    MT.PRESTIGE: PRESTIGE,
    MT.POINTS: POINTS,
    MT.STATUS: STATUS,
}
