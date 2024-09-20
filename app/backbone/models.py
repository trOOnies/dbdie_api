"""SQLAlchemy model definitions."""

from sqlalchemy import Boolean as Bool
from sqlalchemy import Column as C
from sqlalchemy import Date
from sqlalchemy import ForeignKey as FK
from sqlalchemy import Integer as Int
from sqlalchemy import SmallInteger as SmallInt
from sqlalchemy import String as Str
from sqlalchemy.orm import relationship as rel
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from backbone.database import Base
from backbone.options import TABLE_NAMES as TN


class DBDVersion(Base):
    """SQLAlchemy DBD version model."""
    __tablename__ = TN.DBD_VERSION

    id   = C(Int, nullable=False, primary_key=True)
    name = C(Str, nullable=False)

    release_date = C(Date, nullable=True)
    common_name  = C(Str, nullable=True)


class Character(Base):
    """SQLAlchemy character model."""
    __tablename__ = TN.CHARACTER

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    is_killer      = C(Bool, nullable=True)
    base_char_id   = C(SmallInt, nullable=True)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version    = rel("DBDVersion")
    common_name    = C(Str, nullable=True)
    emoji          = C(Str, nullable=True)


class Perk(Base):
    """SQLAlchemy perk model."""
    __tablename__ = TN.PERKS

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    character_id   = C(SmallInt, FK(f"{TN.CHARACTER}.id"), nullable=False)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    emoji          = C(Str, nullable=True)
    character      = rel("Character")
    dbd_version    = rel("DBDVersion")


class ItemType(Base):
    """SQLAlchemy item type model."""
    __tablename__ = TN.ITEM_TYPES

    id            = C(SmallInt, nullable=False, primary_key=True)
    name          = C(Str,      nullable=False)
    emoji         = C(Str,      nullable=True)
    is_for_killer = C(Bool,     nullable=True)


class Item(Base):
    """SQLAlchemy item model."""
    __tablename__ = TN.ITEM

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    type_id        = C(SmallInt, FK(f"{TN.ITEM_TYPES}.id"),  nullable=False)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    type           = rel("ItemType")
    dbd_version    = rel("DBDVersion")


class AddonType(Base):
    """SQLAlchemy addon type model."""
    __tablename__ = TN.ADDONS_TYPES

    id            = C(SmallInt, nullable=False, primary_key=True)
    name          = C(Str,      nullable=False)
    emoji         = C(Str,      nullable=True)
    is_for_killer = C(Bool,     nullable=True)


class Addon(Base):
    """SQLAlchemy addon model."""
    __tablename__ = TN.ADDONS

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    type_id        = C(SmallInt, FK(f"{TN.ADDONS_TYPES}.id"), nullable=False)
    user_id        = C(SmallInt, FK(f"{TN.CHARACTER}.id"),    nullable=False)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"),  nullable=True)
    type           = rel("AddonType")
    user           = rel("Character")
    dbd_version    = rel("DBDVersion")


class OfferingType(Base):
    """SQLAlchemy offering type model."""
    __tablename__ = TN.OFFERING_TYPES

    id            = C(SmallInt, nullable=False, primary_key=True)
    name          = C(Str,      nullable=False)
    emoji         = C(Str,      nullable=True)
    is_for_killer = C(Bool,     nullable=True)


class Offering(Base):
    """SQLAlchemy offering model."""
    __tablename__ = TN.OFFERING

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    type_id        = C(SmallInt, FK(f"{TN.OFFERING_TYPES}.id"), nullable=False)
    user_id        = C(SmallInt, FK(f"{TN.CHARACTER}.id"),      nullable=False)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"),    nullable=True)
    type           = rel("OfferingType")
    user           = rel("Character")
    dbd_version    = rel("DBDVersion")


class Status(Base):
    """SQLAlchemy end player status model."""
    __tablename__ = TN.STATUS

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    character_id   = C(SmallInt, FK(f"{TN.CHARACTER}.id"), nullable=False)
    character      = rel("Character")
    is_dead        = C(Bool, nullable=True)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version    = rel("DBDVersion")
    emoji          = C(Str, nullable=True)


class Match(Base):
    """SQLAlchemy DBD match model."""
    __tablename__ = TN.MATCHES

    id       = C(Int, nullable=False, primary_key=True)
    filename = C(Str, nullable=False)

    match_date     = C(Date, nullable=True)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version    = rel("DBDVersion")
    special_mode   = C(Bool, nullable=True)
    kills          = C(SmallInt, nullable=True)
    date_created   = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_modified = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    user_id        = C(SmallInt, FK(f"{TN.USER}.id"), nullable=True)
    extractor_id   = C(SmallInt, FK(f"{TN.EXTRACTOR}.id"), nullable=True)
    user           = rel("User")
    extractor      = rel("Extractor")


class Labels(Base):
    """SQLAlchemy predictables labels model."""
    __tablename__ = TN.LABELS

    match_id  = C(
        Int,
        FK(f"{TN.MATCHES}.id"),
        primary_key=True,
        nullable=False,
    )
    match     = rel("Match")
    player_id = C(SmallInt, nullable=False, primary_key=True)

    character     = C(SmallInt, nullable=True)
    perk_0        = C(SmallInt, nullable=True)
    perk_1        = C(SmallInt, nullable=True)
    perk_2        = C(SmallInt, nullable=True)
    perk_3        = C(SmallInt, nullable=True)
    item          = C(SmallInt, nullable=True)
    addon_0       = C(SmallInt, nullable=True)
    addon_1       = C(SmallInt, nullable=True)
    offering      = C(SmallInt, nullable=True)
    status        = C(SmallInt, nullable=True)
    points        = C(Int, nullable=True)
    date_modified = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    user_id          = C(SmallInt, FK(f"{TN.USER}.id"), nullable=True)
    extractor_id     = C(SmallInt, FK(f"{TN.EXTRACTOR}.id"), nullable=True)
    user             = rel("User")
    extractor        = rel("Extractor")
    perks_mckd       = C(Bool, nullable=True)
    character_mckd   = C(Bool, nullable=True)
    item_mckd        = C(Bool, nullable=True)
    addons_mckd      = C(Bool, nullable=True)
    offering_mckd    = C(Bool, nullable=True)
    status_mckd      = C(Bool, nullable=True)
    points_mckd      = C(Bool, nullable=True)
    prestige         = C(SmallInt, nullable=True)
    prestige_mckd    = C(Bool, nullable=True)


class User(Base):
    """SQLAlchemy DBDIE user model."""
    __tablename__ = TN.USER

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str, nullable=False, unique=True)


class CropperSwarm(Base):
    """SQLAlchemy CropperSwarm model."""
    __tablename__ = TN.CROPPER_SWARM

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str, nullable=False)

    user_id       = C(SmallInt, FK(f"{TN.USER}.id"), nullable=False)
    img_width     = C(SmallInt, nullable=False)
    img_height    = C(SmallInt, nullable=False)
    dbdv_min_id   = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=False)
    dbdv_max_id   = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    user          = rel("User")
    dbdv_min      = rel("DBDVersion", foreign_keys=[dbdv_min_id])
    dbdv_max      = rel("DBDVersion", foreign_keys=[dbdv_max_id])
    is_for_killer = C(Bool, nullable=True)


class FullModelType(Base):
    """SQLAlchemy full model type model."""
    __tablename__ = TN.FULL_MODEL_TYPES

    id            = C(SmallInt, nullable=False, primary_key=True)
    name          = C(Str, nullable=False)
    model_type    = C(Str, nullable=False)
    is_for_killer = C(Bool, nullable=False)


class Model(Base):
    """SQLAlchemy IEModel model."""
    __tablename__ = TN.MODEL

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str, nullable=False)

    user_id          = C(SmallInt, FK(f"{TN.USER}.id"),             nullable=False)
    fmt_id           = C(SmallInt, FK(f"{TN.FULL_MODEL_TYPES}.id"), nullable=False)
    cropper_swarm_id = C(SmallInt, FK(f"{TN.CROPPER_SWARM}.id"),    nullable=False)
    dbdv_min_id      = C(Int,      FK(f"{TN.DBD_VERSION}.id"),      nullable=False)
    dbdv_max_id      = C(Int,      FK(f"{TN.DBD_VERSION}.id"),      nullable=True)
    special_mode     = C(Bool, nullable=True)
    user             = rel("User")
    fmt              = rel("FullModelType")
    cropper_swarm    = rel("CropperSwarm")
    dbdv_min         = rel("DBDVersion", foreign_keys=[dbdv_min_id])
    dbdv_max         = rel("DBDVersion", foreign_keys=[dbdv_max_id])
    date_created     = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_modified    = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_last_retrained = C(Date, nullable=False)


class Extractor(Base):
    """SQLAlchemy InfoExtractor model."""
    __tablename__ = TN.EXTRACTOR

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str, nullable=False)

    user_id          = C(SmallInt, FK(f"{TN.USER}.id"), nullable=False)
    dbdv_min_id      = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=False)
    dbdv_max_id      = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    special_mode     = C(Bool, nullable=True)
    cropper_swarm_id = C(SmallInt, FK(f"{TN.CROPPER_SWARM}.id"), nullable=False)
    user             = rel("User")
    dbdv_min         = rel("DBDVersion", foreign_keys=[dbdv_min_id])
    dbdv_max         = rel("DBDVersion", foreign_keys=[dbdv_max_id])
    cropper_swarm    = rel("CropperSwarm")

    mid_addons      = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_character   = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_item        = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_offering    = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_perks       = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_points      = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_status      = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    addons_model    = rel("Model", foreign_keys=[mid_addons])
    character_model = rel("Model", foreign_keys=[mid_character])
    item_model      = rel("Model", foreign_keys=[mid_item])
    offering_model  = rel("Model", foreign_keys=[mid_offering])
    perks_model     = rel("Model", foreign_keys=[mid_perks])
    points_model    = rel("Model", foreign_keys=[mid_points])
    status_model    = rel("Model", foreign_keys=[mid_status])

    date_created = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_modified = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_last_retrained = C(Date, nullable=False)
