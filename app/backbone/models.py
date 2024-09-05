"""SQLAlchemy model definitions"""

from backbone.database import Base
from backbone.options import TABLE_NAMES as TN
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


class DBDVersion(Base):
    """SQLAlchemy DBD version model"""
    __tablename__ = TN.DBD_VERSION

    id = C(Int, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    release_date = C(Date, nullable=True)
    common_name = C(Str, nullable=True)


class Character(Base):
    """SQLAlchemy character model"""
    __tablename__ = TN.CHARACTER

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    is_killer = C(Bool, nullable=True)
    base_char_id = C(SmallInt, nullable=True)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version = rel("DBDVersion")
    common_name = C(Str, nullable=True)
    emoji = C(Str, nullable=True)


class Perk(Base):
    """SQLAlchemy perk model"""
    __tablename__ = TN.PERKS

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    character_id = C(SmallInt, FK(f"{TN.CHARACTER}.id"), nullable=False)
    character = rel("Character")
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version = rel("DBDVersion")
    emoji = C(Str, nullable=True)


class ItemType(Base):
    """SQLAlchemy item type model"""
    __tablename__ = TN.ITEM_TYPES

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    emoji = C(Str, nullable=True)


class Item(Base):
    """SQLAlchemy item model"""
    __tablename__ = TN.ITEM

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    type_id = C(SmallInt, FK(f"{TN.ITEM_TYPES}.id"), nullable=False)
    type = rel("ItemType")
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class AddonType(Base):
    """SQLAlchemy addon type model"""
    __tablename__ = TN.ADDONS_TYPES

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    emoji = C(Str, nullable=True)


class Addon(Base):
    """SQLAlchemy addon model"""
    __tablename__ = TN.ADDONS

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    type_id = C(SmallInt, FK(f"{TN.ADDONS_TYPES}.id"), nullable=False)
    type = rel("AddonType")
    user_id = C(SmallInt, FK(f"{TN.CHARACTER}.id"), nullable=False)
    user = rel("Character")
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class OfferingType(Base):
    """SQLAlchemy offering type model"""
    __tablename__ = TN.OFFERING_TYPES

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    emoji = C(Str, nullable=True)


class Offering(Base):
    """SQLAlchemy offering model"""
    __tablename__ = TN.OFFERING

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    type_id = C(SmallInt, FK(f"{TN.OFFERING_TYPES}.id"), nullable=False)
    type = rel("OfferingType")
    user_id = C(SmallInt, FK(f"{TN.CHARACTER}.id"), nullable=False)
    user = rel("Character")
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class Status(Base):
    """SQLAlchemy end player status model"""
    __tablename__ = TN.STATUS

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    character_id = C(SmallInt, FK(f"{TN.CHARACTER}.id"), nullable=False)
    character = rel("Character")
    is_dead = C(Bool, nullable=True)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version = rel("DBDVersion")
    emoji = C(Str, nullable=True)


class Match(Base):
    """SQLAlchemy match model"""
    __tablename__ = TN.MATCHES

    id = C(Int, primary_key=True, nullable=False)
    filename = C(Str, nullable=False)
    match_date = C(Date, nullable=True)
    dbd_version_id = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbd_version = rel("DBDVersion")
    special_mode = C(Bool, nullable=True)
    user = C(Str, nullable=True)
    extractor = C(Str, nullable=True)
    kills = C(SmallInt, nullable=True)
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


class Labels(Base):
    """SQLAlchemy labels model"""
    __tablename__ = TN.LABELS

    match_id = C(
        Int,
        FK(f"{TN.MATCHES}.id"),
        primary_key=True,
        nullable=False,
    )
    match = rel("Match")
    player_id = C(SmallInt, primary_key=True, nullable=False)
    character = C(SmallInt, nullable=True)
    perk_0 = C(SmallInt, nullable=True)
    perk_1 = C(SmallInt, nullable=True)
    perk_2 = C(SmallInt, nullable=True)
    perk_3 = C(SmallInt, nullable=True)
    item = C(SmallInt, nullable=True)
    addon_0 = C(SmallInt, nullable=True)
    addon_1 = C(SmallInt, nullable=True)
    offering = C(SmallInt, nullable=True)
    status = C(SmallInt, nullable=True)
    points = C(Int, nullable=True)
    date_modified = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
