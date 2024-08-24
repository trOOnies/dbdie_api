from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from backbone.database import Base


class DBDVersion(Base):
    __tablename__ = "dbd_version"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    release_date = Column(Date, nullable=True)


class Character(Base):
    __tablename__ = "character"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    is_killer = Column(Boolean, nullable=True)
    base_char_id = Column(Integer, nullable=True)
    dbd_version_id = Column(Integer, ForeignKey("dbd_version.id"), nullable=True)
    dbd_version = relationship("DBDVersion")


class Perk(Base):
    __tablename__ = "perks"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    character = relationship("Character")
    dbd_version_id = Column(Integer, ForeignKey("dbd_version.id"), nullable=True)
    dbd_version = relationship("DBDVersion")


class ItemType(Base):
    __tablename__ = "item_types"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey("item_types.id"), nullable=False)
    type = relationship("ItemType")


class AddonType(Base):
    __tablename__ = "addons_types"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Addon(Base):
    __tablename__ = "addons"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey("addons_types.id"), nullable=False)
    type = relationship("AddonType")
    user_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    user = relationship("Character")


class OfferingType(Base):
    __tablename__ = "offering_types"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Offering(Base):
    __tablename__ = "offering"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey("offering_types.id"), nullable=False)
    type = relationship("OfferingType")
    user_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    user = relationship("Character")


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    character = relationship("Character")
    is_dead = Column(Boolean, nullable=True)


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, nullable=False)
    filename = Column(String, nullable=False)
    match_date = Column(Date, nullable=True)
    dbd_version_id = Column(Integer, ForeignKey("dbd_version.id"), nullable=True)
    dbd_version = relationship("DBDVersion")
    special_mode = Column(Boolean, nullable=True)
    user = Column(String, nullable=True)
    extractor = Column(String, nullable=True)
    kills = Column(Integer, nullable=True)
    date_created = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_modified = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
