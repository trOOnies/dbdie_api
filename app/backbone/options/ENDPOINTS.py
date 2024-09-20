"""DBDIE API high-level endpoints."""

from dbdie_ml.options import MODEL_TYPES as MT

ADDONS      = "/addons"
CHARACTER   = "/character"
ITEM        = "/item"
OFFERING    = "/offering"
PERKS       = "/perks"
STATUS      = "/status"
PLAYERS     = "/players"
DBD_VERSION = "/dbd-version"
MATCHES     = "/matches"
LABELS      = "/labels"

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
    MT.STATUS: STATUS,
}
