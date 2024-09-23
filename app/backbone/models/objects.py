"""SQLAlchemy model definitions for DBDIE related objects."""

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

    user_id       = C(SmallInt, FK(f"{TN.USER}.id"),        nullable=False)
    img_width     = C(SmallInt, nullable=False)
    img_height    = C(SmallInt, nullable=False)
    dbdv_min_id   = C(Int,      FK(f"{TN.DBD_VERSION}.id"), nullable=False)
    dbdv_max_id   = C(Int,      FK(f"{TN.DBD_VERSION}.id"), nullable=True)

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

    user_id          = C(SmallInt, FK(f"{TN.USER}.id"),          nullable=False)
    dbdv_min_id      = C(Int,      FK(f"{TN.DBD_VERSION}.id"),   nullable=False)
    dbdv_max_id      = C(Int,      FK(f"{TN.DBD_VERSION}.id"),   nullable=True)
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
    mid_prestige    = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_status      = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    addons_model    = rel("Model", foreign_keys=[mid_addons])
    character_model = rel("Model", foreign_keys=[mid_character])
    item_model      = rel("Model", foreign_keys=[mid_item])
    offering_model  = rel("Model", foreign_keys=[mid_offering])
    perks_model     = rel("Model", foreign_keys=[mid_perks])
    points_model    = rel("Model", foreign_keys=[mid_points])
    prestige_model  = rel("Model", foreign_keys=[mid_prestige])
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
