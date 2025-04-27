"""Table names as seen in the DBDIE database."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dbdie_classes.base import TableName

ADDONS           : "TableName" = "addons"
ADDONS_TYPES     : "TableName" = "addons_types"
CHARACTER        : "TableName" = "character"
CROPPER_SWARM    : "TableName" = "cropper_swarm"
DBD_VERSION      : "TableName" = "dbd_version"
EXTRACTOR        : "TableName" = "extractor"
FULL_MODEL_TYPES : "TableName" = "full_model_types"
ITEM             : "TableName" = "item"
ITEM_TYPES       : "TableName" = "item_types"
LABELS           : "TableName" = "labels"
MATCHES          : "TableName" = "matches"
MODEL            : "TableName" = "model"
OFFERING         : "TableName" = "offering"
OFFERING_TYPES   : "TableName" = "offering_types"
PERKS            : "TableName" = "perks"
RARITY           : "TableName" = "rarity"
STATUS           : "TableName" = "status"
USER             : "TableName" = "user"

PREDICTABLES: list["TableName"] = [
    ADDONS,
    CHARACTER,
    ITEM,
    OFFERING,
    PERKS,
    STATUS,
]

PREDICTABLE_TYPES: list["TableName"] = [
    ADDONS_TYPES,
    ITEM_TYPES,
    OFFERING_TYPES,
]

DBDIE_OBJECTS: list["TableName"] = [
    CROPPER_SWARM,
    EXTRACTOR,
    MODEL,
    USER,
]

NAME_FILTERED_TABLENAMES: set["TableName"] = {
    ADDONS,
    CHARACTER,
    DBD_VERSION,
    ITEM,
    OFFERING,
    PERKS,
    STATUS,
}
