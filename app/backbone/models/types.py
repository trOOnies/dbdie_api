"""SQLAlchemy model definitions for the types of a predictable."""

from sqlalchemy import Boolean as Bool
from sqlalchemy import Column as C
from sqlalchemy import SmallInteger as SmallInt
from sqlalchemy import String as Str

from backbone.database import Base
from backbone.options import TABLE_NAMES as TN


class ItemType(Base):
    """SQLAlchemy item type model."""
    __tablename__ = TN.ITEM_TYPES

    id            = C(SmallInt, nullable=False, primary_key=True)
    name          = C(Str,      nullable=False)
    emoji         = C(Str,      nullable=True)
    is_for_killer = C(Bool,     nullable=True)


class AddonType(Base):
    """SQLAlchemy addon type model."""
    __tablename__ = TN.ADDONS_TYPES

    id            = C(SmallInt, nullable=False, primary_key=True)
    name          = C(Str,      nullable=False)
    emoji         = C(Str,      nullable=True)
    is_for_killer = C(Bool,     nullable=True)


class OfferingType(Base):
    """SQLAlchemy offering type model."""
    __tablename__ = TN.OFFERING_TYPES

    id            = C(SmallInt, nullable=False, primary_key=True)
    name          = C(Str,      nullable=False)
    emoji         = C(Str,      nullable=True)
    is_for_killer = C(Bool,     nullable=True)


class Rarity(Base):
    """SQLAlchemy rarity model."""
    __tablename__ = TN.RARITY

    id    = C(SmallInt, nullable=False, primary_key=True)
    name  = C(Str,      nullable=False, unique=True)
    color = C(Str,      nullable=False)
    emoji = C(Str,      nullable=True)
