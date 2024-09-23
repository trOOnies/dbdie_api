"""DBDIE API high-level endpoints."""

from dbdie_classes.options import MODEL_TYPES as MT

ADDONS      = "/addons"
CHARACTER   = "/character"
ITEM        = "/item"
OFFERING    = "/offering"
PERKS       = "/perks"
POINTS      = "/points"
PRESTIGE    = "/prestige"
STATUS      = "/status"

# Groupings
DBD_VERSION = "/dbd-version"
MATCHES     = "/matches"
PLAYERS     = "/players"
LABELS      = "/labels"

# DBDIE objects
EXTRACTOR   = "/extractor"
MODELS      = "/models"

# Processes
CROP        = "/crop"
EXTRACT     = "/extract"
BACKUP      = "/backup"
TRAIN       = "/train"

MT_TO_ENDPOINT = {
    MT.ADDONS: ADDONS,
    MT.CHARACTER: CHARACTER,
    MT.ITEM: ITEM,
    MT.OFFERING: OFFERING,
    MT.PERKS: PERKS,
    MT.PRESTIGE: PRESTIGE,
    MT.POINTS: POINTS,
    MT.STATUS: STATUS,
}
