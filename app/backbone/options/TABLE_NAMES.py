"""Table names as seen in the DBDIE database."""

ADDONS           = "addons"
ADDONS_TYPES     = "addons_types"
CHARACTER        = "character"
CROPPER_SWARM    = "cropper_swarm"
DBD_VERSION      = "dbd_version"
EXTRACTOR        = "extractor"
FULL_MODEL_TYPES = "full_model_types"
ITEM             = "item"
ITEM_TYPES       = "item_types"
LABELS           = "labels"
MATCHES          = "matches"
MODEL            = "model"
OFFERING         = "offering"
OFFERING_TYPES   = "offering_types"
PERKS            = "perks"
STATUS           = "status"
USER             = "user"

PREDICTABLES = [
    ADDONS,
    CHARACTER,
    ITEM,
    OFFERING,
    PERKS,
    STATUS,
]

PREDICTABLE_TYPES = [
    ADDONS_TYPES,
    ITEM_TYPES,
    OFFERING_TYPES,
]

DBDIE_OBJECTS = [
    CROPPER_SWARM,
    EXTRACTOR,
    MODEL,
    USER,
]
