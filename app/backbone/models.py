from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backbone.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    is_killer = Column(Boolean, nullable=True)


class Perk(Base):
    __tablename__ = "perks"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    character_id = Column(
        Integer,
        ForeignKey("characters.id"),
        nullable=False
    )
    character = relationship("Character")


class ItemType(Base):
    __tablename__ = "itemstypes"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type_id = Column(
        Integer,
        ForeignKey("itemstypes.id"),
        nullable=False
    )
    type = relationship("ItemType")


class AddonType(Base):
    __tablename__ = "addonstypes"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Addon(Base):
    __tablename__ = "addons"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type_id = Column(
        Integer,
        ForeignKey("addonstypes.id"),
        nullable=False
    )
    type = relationship("AddonType")
    user_id = Column(
        Integer,
        ForeignKey("characters.id"),
        nullable=False
    )
    user = relationship("Character")



class OfferingType(Base):
    __tablename__ = "offeringstypes"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Offering(Base):
    __tablename__ = "offerings"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type_id = Column(
        Integer,
        ForeignKey("offeringstypes.id"),
        nullable=False
    )
    type = relationship("OfferingType")
    user_id = Column(
        Integer,
        ForeignKey("characters.id"),
        nullable=False
    )
    user = relationship("Character")


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    character_id = Column(
        Integer,
        ForeignKey("characters.id"),
        nullable=False
    )
    character = relationship("Character")
    is_dead = Column(Boolean, nullable=True)
