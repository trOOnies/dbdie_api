from sqlalchemy import (
    Boolean as Bool,
    Column as C,
    Date,
    ForeignKey as FK,
    Integer as Int,
    SmallInteger as SmallInt,
    String as Str,
)
from sqlalchemy.orm import relationship as rel
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from backbone.database import Base


class DBDVersion(Base):
    __tablename__ = "dbd_version"

    id = C(Int, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    release_date = C(Date, nullable=True)


class Character(Base):
    __tablename__ = "character"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    is_killer = C(Bool, nullable=True)
    base_char_id = C(SmallInt, nullable=True)
    dbd_version_id = C(Int, FK("dbd_version.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class Perk(Base):
    __tablename__ = "perks"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    character_id = C(SmallInt, FK("character.id"), nullable=False)
    character = rel("Character")
    dbd_version_id = C(Int, FK("dbd_version.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class ItemType(Base):
    __tablename__ = "item_types"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)


class Item(Base):
    __tablename__ = "item"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    type_id = C(SmallInt, FK("item_types.id"), nullable=False)
    type = rel("ItemType")
    dbd_version_id = C(Int, FK("dbd_version.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class AddonType(Base):
    __tablename__ = "addons_types"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)


class Addon(Base):
    __tablename__ = "addons"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    type_id = C(SmallInt, FK("addons_types.id"), nullable=False)
    type = rel("AddonType")
    user_id = C(SmallInt, FK("character.id"), nullable=False)
    user = rel("Character")
    dbd_version_id = C(Int, FK("dbd_version.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class OfferingType(Base):
    __tablename__ = "offering_types"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)


class Offering(Base):
    __tablename__ = "offering"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    type_id = C(SmallInt, FK("offering_types.id"), nullable=False)
    type = rel("OfferingType")
    user_id = C(SmallInt, FK("character.id"), nullable=False)
    user = rel("Character")
    dbd_version_id = C(Int, FK("dbd_version.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class Status(Base):
    __tablename__ = "status"

    id = C(SmallInt, primary_key=True, nullable=False)
    name = C(Str, nullable=False)
    character_id = C(SmallInt, FK("character.id"), nullable=False)
    character = rel("Character")
    is_dead = C(Bool, nullable=True)
    dbd_version_id = C(Int, FK("dbd_version.id"), nullable=True)
    dbd_version = rel("DBDVersion")


class Match(Base):
    __tablename__ = "matches"

    id = C(Int, primary_key=True, nullable=False)
    filename = C(Str, nullable=False)
    match_date = C(Date, nullable=True)
    dbd_version_id = C(Int, FK("dbd_version.id"), nullable=True)
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
    __tablename__ = "labels"

    match_id = C(
        Int,
        FK("matches.id"),
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
