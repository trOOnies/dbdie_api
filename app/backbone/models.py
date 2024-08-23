from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
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


class Perk(Base):
    __tablename__ = "perks"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    character_id = Column(Integer, ForeignKey("character.id"), nullable=False)
    character = relationship("Character")
    dbd_version_id = Column(Integer, ForeignKey("dbd_version.id"), nullable=True)


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
