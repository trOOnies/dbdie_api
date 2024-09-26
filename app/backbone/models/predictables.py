"""SQLAlchemy model definitions for predictables."""

from sqlalchemy import Boolean as Bool
from sqlalchemy import Column as C
from sqlalchemy import ForeignKey as FK
from sqlalchemy import Integer as Int
from sqlalchemy import SmallInteger as SmallInt
from sqlalchemy import String as Str
from sqlalchemy.orm import relationship as rel

from backbone.database import Base
from backbone.models.types import (
    AddonType,  # noqa: F401
    ItemType,  # noqa: F401
    OfferingType,  # noqa: F401
    Rarity,  # noqa: F401
)
from backbone.models.helpers import DBDVersion  # noqa: F401
from backbone.options import TABLE_NAMES as TN


class Item(Base):
    """SQLAlchemy item model."""
    __tablename__ = TN.ITEM

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    type_id        = C(SmallInt, FK(f"{TN.ITEM_TYPES}.id"),  nullable=False)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    rarity_id      = C(SmallInt, FK(f"{TN.RARITY}.id"),      nullable=True)

    type           = rel("ItemType")
    dbd_version    = rel("DBDVersion")
    rarity         = rel("Rarity")


class Character(Base):
    """SQLAlchemy character model."""
    __tablename__ = TN.CHARACTER

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)  # TODO: add unique (and with alembic)

    is_killer      = C(Bool,     nullable=True)
    base_char_id   = C(SmallInt, nullable=True)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version    = rel("DBDVersion")

    common_name = C(Str,      nullable=True)
    emoji       = C(Str,      nullable=True)

    power_id    = C(SmallInt, FK(f"{TN.ITEM}.id"), nullable=True)
    power       = rel("Item")


class Addon(Base):
    """SQLAlchemy addon model."""
    __tablename__ = TN.ADDONS

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    type_id        = C(SmallInt, FK(f"{TN.ADDONS_TYPES}.id"), nullable=False)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"),  nullable=True)
    item_id        = C(SmallInt, FK(f"{TN.ITEM}.id"),         nullable=False)
    rarity_id      = C(SmallInt, FK(f"{TN.RARITY}.id"),       nullable=True)

    type           = rel("AddonType")
    dbd_version    = rel("DBDVersion")
    item           = rel("Item")
    rarity         = rel("Rarity")


class Perk(Base):
    """SQLAlchemy perk model."""
    __tablename__ = TN.PERKS

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    character_id   = C(SmallInt, FK(f"{TN.CHARACTER}.id"),   nullable=False)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    emoji          = C(Str, nullable=True)
    character      = rel("Character")
    dbd_version    = rel("DBDVersion")


class Offering(Base):
    """SQLAlchemy offering model."""
    __tablename__ = TN.OFFERING

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    type_id        = C(SmallInt, FK(f"{TN.OFFERING_TYPES}.id"), nullable=False)
    user_id        = C(SmallInt, FK(f"{TN.CHARACTER}.id"),      nullable=False)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"),    nullable=True)
    rarity_id      = C(SmallInt, FK(f"{TN.RARITY}.id"),         nullable=True)

    type           = rel("OfferingType")
    user           = rel("Character")
    dbd_version    = rel("DBDVersion")
    rarity         = rel("Rarity")


class Status(Base):
    """SQLAlchemy end player status model."""
    __tablename__ = TN.STATUS

    id   = C(SmallInt, nullable=False, primary_key=True)
    name = C(Str,      nullable=False)

    character_id   = C(SmallInt, FK(f"{TN.CHARACTER}.id"),  nullable=False)
    is_dead        = C(Bool, nullable=True)
    dbd_version_id = C(Int,      FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    emoji          = C(Str,  nullable=True)

    character      = rel("Character")
    dbd_version    = rel("DBDVersion")
