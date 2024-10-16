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
from backbone.models.helpers import DBDVersion  # noqa: F401
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

    ifk = C(Bool, nullable=True)


class FullModelType(Base):
    """SQLAlchemy full model type model."""
    __tablename__ = TN.FULL_MODEL_TYPES

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str, nullable=False)
    mt   = C(Str, nullable=False)
    ifk  = C(Bool, nullable=True)


class Model(Base):
    """SQLAlchemy IEModel model."""
    __tablename__ = TN.MODEL

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str, nullable=False)

    user_id       = C(SmallInt, FK(f"{TN.USER}.id"),             nullable=False)
    fmt_id        = C(SmallInt, FK(f"{TN.FULL_MODEL_TYPES}.id"), nullable=False)
    cps_id        = C(SmallInt, FK(f"{TN.CROPPER_SWARM}.id"),    nullable=False)
    dbdv_min_id   = C(Int,      FK(f"{TN.DBD_VERSION}.id"),      nullable=False)
    dbdv_max_id   = C(Int,      FK(f"{TN.DBD_VERSION}.id"),      nullable=True)
    special_mode  = C(Bool, nullable=True)
    user          = rel("User")
    fmt           = rel("FullModelType")
    cropper_swarm = rel("CropperSwarm")
    dbdv_min      = rel("DBDVersion", foreign_keys=[dbdv_min_id])
    dbdv_max      = rel("DBDVersion", foreign_keys=[dbdv_max_id])
    date_created  = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_modified    = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_last_trained = C(Date, nullable=False)


class Extractor(Base):
    """SQLAlchemy InfoExtractor model."""
    __tablename__ = TN.EXTRACTOR

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str, nullable=False)

    user_id       = C(SmallInt, FK(f"{TN.USER}.id"),          nullable=False)
    dbdv_min_id   = C(Int,      FK(f"{TN.DBD_VERSION}.id"),   nullable=False)
    dbdv_max_id   = C(Int,      FK(f"{TN.DBD_VERSION}.id"),   nullable=True)
    special_mode  = C(Bool, nullable=True)
    cps_id        = C(SmallInt, FK(f"{TN.CROPPER_SWARM}.id"), nullable=False)

    user          = rel("User")
    dbdv_min      = rel("DBDVersion", foreign_keys=[dbdv_min_id])
    dbdv_max      = rel("DBDVersion", foreign_keys=[dbdv_max_id])
    cropper_swarm = rel("CropperSwarm")

    mid_0  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_1  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_2  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_3  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_4  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_5  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_6  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_7  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_8  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_9  = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_10 = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_11 = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)
    mid_12 = C(SmallInt, FK(f"{TN.MODEL}.id"), nullable=True)

    model_0  = rel("Model", foreign_keys=[mid_0])
    model_1  = rel("Model", foreign_keys=[mid_1])
    model_2  = rel("Model", foreign_keys=[mid_2])
    model_3  = rel("Model", foreign_keys=[mid_3])
    model_4  = rel("Model", foreign_keys=[mid_4])
    model_5  = rel("Model", foreign_keys=[mid_5])
    model_6  = rel("Model", foreign_keys=[mid_6])
    model_7  = rel("Model", foreign_keys=[mid_7])
    model_8  = rel("Model", foreign_keys=[mid_8])
    model_9  = rel("Model", foreign_keys=[mid_9])
    model_10 = rel("Model", foreign_keys=[mid_10])
    model_11 = rel("Model", foreign_keys=[mid_11])
    model_12 = rel("Model", foreign_keys=[mid_12])

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
    date_last_trained = C(Date, nullable=False)
